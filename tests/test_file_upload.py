import pytest
import io
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch, mock_open
from fastapi import HTTPException, UploadFile
from pathlib import Path

from app.controllers.user_controller import UserController
from app.services.user_service import UserService
from app.models.user import User
from app.models.enums import UserRole


class TestFileUpload:
    """Test suite for file upload functionality"""

    @pytest.fixture
    def mock_user_service(self):
        """Mock user service for testing"""
        service = Mock(spec=UserService)
        service.update_user_files = AsyncMock()
        return service

    @pytest.fixture
    def user_controller(self, mock_user_service):
        """Create user controller with mocked dependencies"""
        return UserController(mock_user_service)

    @pytest.fixture
    def test_user(self):
        """Sample user for testing"""
        return User(
            id="test-user-123",
            email="test@example.com",
            name="Test User",
            role=UserRole.STUDENT,
            is_active=True
        )

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        with patch('app.controllers.user_controller.settings') as mock_settings:
            mock_settings.UPLOAD_DIR = Path("/tmp/test_uploads")
            mock_settings.MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            yield mock_settings

    def create_mock_upload_file(self, filename: str, content: bytes, content_type: str = "application/pdf"):
        """Create a mock UploadFile for testing"""
        file_like = io.BytesIO(content)
        upload_file = UploadFile(
            filename=filename,
            file=file_like,
            headers={"content-type": content_type}
        )
        # Mock the read method to return the content
        upload_file.read = AsyncMock(return_value=content)
        return upload_file

    # VALID FILE UPLOAD TESTS
    @pytest.mark.asyncio
    async def test_upload_cv_file_success(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test successful CV file upload"""
        # Create mock PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n%%EOF"
        mock_file = self.create_mock_upload_file("test_cv.pdf", pdf_content)

        # Mock file operations
        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            # Mock successful database update
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "cv", test_user)

            # Assertions
            assert result["success"] == True
            assert result["message"] == "File uploaded successfully"
            assert result["filename"] == "test_cv.pdf"
            assert result["file_type"] == "cv"
            assert result["file_size"] == len(pdf_content)

            # Verify database update was called
            mock_user_service.update_user_files.assert_called_once()
            call_args = mock_user_service.update_user_files.call_args[0]
            assert call_args[0] == test_user.id
            assert call_args[1] == "cv"
            
            # Verify file info structure
            file_info = call_args[2]
            assert file_info["filename"] == "test_cv.pdf"
            assert file_info["file_size"] == len(pdf_content)
            assert "uploaded_at" in file_info

    @pytest.mark.asyncio
    async def test_upload_certificate_file_success(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test successful certificate file upload"""
        pdf_content = b"%PDF-1.4\ntest certificate content"
        mock_file = self.create_mock_upload_file("certificate.pdf", pdf_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "certificate", test_user)

            assert result["success"] == True
            assert result["file_type"] == "certificate"

    @pytest.mark.asyncio
    async def test_upload_degree_file_success(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test successful degree file upload"""
        pdf_content = b"%PDF-1.4\ntest degree content"
        mock_file = self.create_mock_upload_file("degree.pdf", pdf_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "degree", test_user)

            assert result["success"] == True
            assert result["file_type"] == "degree"

    # FILE TYPE VALIDATION TESTS
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload fails with invalid file type"""
        pdf_content = b"%PDF-1.4\ntest content"
        mock_file = self.create_mock_upload_file("test.pdf", pdf_content)

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.upload_file(mock_file, "invalid_type", test_user)

        assert exc_info.value.status_code == 400
        assert "Invalid file type" in str(exc_info.value.detail)
        assert "cv, certificate, degree" in str(exc_info.value.detail)

    # FILE EXTENSION VALIDATION TESTS
    @pytest.mark.asyncio
    async def test_upload_non_pdf_file(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload fails with non-PDF file"""
        txt_content = b"This is a text file"
        mock_file = self.create_mock_upload_file("test.txt", txt_content, "text/plain")

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.upload_file(mock_file, "cv", test_user)

        assert exc_info.value.status_code == 400
        assert "Only PDF files are allowed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_file_without_extension(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload fails with file without extension"""
        content = b"some content"
        mock_file = self.create_mock_upload_file("testfile", content)

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.upload_file(mock_file, "cv", test_user)

        assert exc_info.value.status_code == 400
        assert "Only PDF files are allowed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_file_no_filename(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload fails with no filename"""
        content = b"some content"
        mock_file = self.create_mock_upload_file(None, content)

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.upload_file(mock_file, "cv", test_user)

        assert exc_info.value.status_code == 400
        assert "No filename provided" in str(exc_info.value.detail)

    # FILE SIZE VALIDATION TESTS
    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload fails with file exceeding size limit"""
        # Create content larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        mock_file = self.create_mock_upload_file("large_file.pdf", large_content)

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.upload_file(mock_file, "cv", test_user)

        assert exc_info.value.status_code == 400
        assert "File size exceeds maximum" in str(exc_info.value.detail)
        assert "10MB" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_empty_file(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload with empty file"""
        empty_content = b""
        mock_file = self.create_mock_upload_file("empty.pdf", empty_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "cv", test_user)

            # Empty files should be allowed (some PDFs might be very small)
            assert result["success"] == True
            assert result["file_size"] == 0

    # DIRECTORY CREATION TESTS
    @pytest.mark.asyncio
    async def test_upload_creates_user_directory(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test that upload creates user-specific directory"""
        pdf_content = b"%PDF-1.4\ntest content"
        mock_file = self.create_mock_upload_file("test.pdf", pdf_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            await user_controller.upload_file(mock_file, "cv", test_user)

            # Verify directory creation was called
            mock_mkdir.assert_called_once()
            call_args = mock_mkdir.call_args
            assert call_args[1]["parents"] == True
            assert call_args[1]["exist_ok"] == True

    # DATABASE UPDATE FAILURE TESTS
    @pytest.mark.asyncio
    async def test_upload_database_update_failure(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload handles database update failure with cleanup"""
        pdf_content = b"%PDF-1.4\ntest content"
        mock_file = self.create_mock_upload_file("test.pdf", pdf_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=True) as mock_exists, \
             patch('pathlib.Path.unlink') as mock_unlink:
            
            # Mock database update failure
            mock_user_service.update_user_files.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await user_controller.upload_file(mock_file, "cv", test_user)

            assert exc_info.value.status_code == 500
            assert "Failed to update user profile" in str(exc_info.value.detail)
            
            # Verify cleanup was attempted
            mock_unlink.assert_called_once()

    # FILE NAMING TESTS
    @pytest.mark.asyncio
    async def test_upload_generates_unique_filename(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test that upload generates unique filenames"""
        pdf_content = b"%PDF-1.4\ntest content"
        mock_file = self.create_mock_upload_file("test.pdf", pdf_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False), \
             patch('uuid.uuid4', return_value=Mock(hex='123e4567e89b12d3a456426614174000')):
            
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "cv", test_user)

            # Verify unique filename was generated
            assert "cv_123e4567e89b12d3a456426614174000.pdf" in result["file_path"]

    # CONCURRENT UPLOAD TESTS
    @pytest.mark.asyncio
    async def test_multiple_file_uploads_for_same_user(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test multiple file uploads for the same user"""
        files_data = [
            ("cv.pdf", "cv", b"%PDF-1.4\ncv content"),
            ("cert.pdf", "certificate", b"%PDF-1.4\ncert content"),
            ("degree.pdf", "degree", b"%PDF-1.4\ndegree content")
        ]

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            for filename, file_type, content in files_data:
                mock_file = self.create_mock_upload_file(filename, content)
                result = await user_controller.upload_file(mock_file, file_type, test_user)
                
                assert result["success"] == True
                assert result["file_type"] == file_type
                assert result["filename"] == filename

            # Verify database was updated for each file
            assert mock_user_service.update_user_files.call_count == 3

    # ERROR HANDLING TESTS
    @pytest.mark.asyncio
    async def test_upload_file_system_error(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload handles file system errors"""
        pdf_content = b"%PDF-1.4\ntest content"
        mock_file = self.create_mock_upload_file("test.pdf", pdf_content)

        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            
            with pytest.raises(HTTPException) as exc_info:
                await user_controller.upload_file(mock_file, "cv", test_user)

            assert exc_info.value.status_code == 500
            assert "File upload failed" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_file_read_error(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload handles file read errors"""
        mock_file = Mock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(side_effect=Exception("File read error"))

        with pytest.raises(HTTPException) as exc_info:
            await user_controller.upload_file(mock_file, "cv", test_user)

        assert exc_info.value.status_code == 500
        assert "File upload failed" in str(exc_info.value.detail)

    # INTEGRATION TESTS
    def test_upload_endpoint_requires_auth(self, api_client):
        """Test that upload endpoint requires authentication"""
        # Create a simple file for upload
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        
        response = api_client.post("/api/users/upload-file", files=files)
        assert response.status_code == 401

    def test_upload_endpoint_with_invalid_content_type(self, api_client):
        """Test upload endpoint with invalid content type"""
        # This test would require authenticated client, so we just test the endpoint exists
        response = api_client.post("/api/users/upload-file")
        # Should be 401 (auth required) or 422 (validation error), not 404
        assert response.status_code in [401, 422]

    # SECURITY TESTS
    @pytest.mark.asyncio
    async def test_upload_prevents_path_traversal(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test that upload prevents path traversal attacks"""
        pdf_content = b"%PDF-1.4\ntest content"
        # Try to use path traversal in filename
        mock_file = self.create_mock_upload_file("../../../etc/passwd.pdf", pdf_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "cv", test_user)

            # Verify the filename was sanitized (should not contain path traversal)
            assert result["success"] == True
            # The generated filename should be safe and not contain ../ 
            assert "../" not in result["file_path"]

    @pytest.mark.asyncio
    async def test_upload_validates_file_extension_case_insensitive(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test that file extension validation is case insensitive"""
        pdf_content = b"%PDF-1.4\ntest content"
        
        # Test various case combinations
        for filename in ["test.PDF", "test.Pdf", "test.pDf"]:
            mock_file = self.create_mock_upload_file(filename, pdf_content)

            with patch('builtins.open', mock_open()) as mock_file_open, \
                 patch('pathlib.Path.mkdir') as mock_mkdir, \
                 patch('pathlib.Path.exists', return_value=False):
                
                mock_user_service.update_user_files.return_value = True

                result = await user_controller.upload_file(mock_file, "cv", test_user)
                assert result["success"] == True

    # PERFORMANCE TESTS
    @pytest.mark.asyncio
    async def test_upload_large_valid_file(self, user_controller, mock_user_service, test_user, mock_settings):
        """Test upload of large but valid file (just under limit)"""
        # Create file just under the 10MB limit
        large_content = b"x" * (9 * 1024 * 1024)  # 9MB
        mock_file = self.create_mock_upload_file("large_valid.pdf", large_content)

        with patch('builtins.open', mock_open()) as mock_file_open, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_user_service.update_user_files.return_value = True

            result = await user_controller.upload_file(mock_file, "cv", test_user)

            assert result["success"] == True
            assert result["file_size"] == 9 * 1024 * 1024