import requests
import json
from datetime import datetime

class ContentVerificationTester:
    def __init__(self, base_url="https://jobhub-paraguay.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.issues = []
        self.successes = []

    def log_issue(self, category, message):
        self.issues.append(f"❌ {category}: {message}")
        print(f"❌ {category}: {message}")

    def log_success(self, category, message):
        self.successes.append(f"✅ {category}: {message}")
        print(f"✅ {category}: {message}")

    def verify_courses_content(self):
        """Verify courses content quality and quantity"""
        print("\n" + "="*60)
        print("🔍 VERIFYING COURSES CONTENT")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/courses")
            courses = response.json()
            
            # Check quantity
            if len(courses) >= 20:
                self.log_success("Courses Quantity", f"Found {len(courses)} courses (requirement: 20+)")
            else:
                self.log_issue("Courses Quantity", f"Only {len(courses)} courses found, expected 20+")
            
            # Check for real providers mentioned in requirements
            expected_providers = ["Claseflix", "Google Skillshop", "Programación ATS"]
            found_providers = set()
            categories = set()
            
            for course in courses:
                found_providers.add(course.get('provider', ''))
                categories.add(course.get('category', ''))
                
                # Check if course has required fields
                required_fields = ['title', 'description', 'provider', 'url', 'category']
                missing_fields = [field for field in required_fields if not course.get(field)]
                if missing_fields:
                    self.log_issue("Course Data", f"Course '{course.get('title', 'Unknown')}' missing: {missing_fields}")
            
            # Check for expected providers
            for provider in expected_providers:
                if any(provider.lower() in fp.lower() for fp in found_providers):
                    self.log_success("Course Providers", f"Found expected provider: {provider}")
                else:
                    self.log_issue("Course Providers", f"Missing expected provider: {provider}")
            
            # Check category diversity
            if len(categories) >= 5:
                self.log_success("Course Categories", f"Good diversity: {len(categories)} categories found")
                print(f"   Categories: {', '.join(sorted(categories))}")
            else:
                self.log_issue("Course Categories", f"Limited diversity: only {len(categories)} categories")
            
            return len(courses) >= 20
            
        except Exception as e:
            self.log_issue("Courses API", f"Failed to fetch courses: {str(e)}")
            return False

    def verify_events_content(self):
        """Verify events content quality and quantity"""
        print("\n" + "="*60)
        print("🔍 VERIFYING EVENTS CONTENT")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/events")
            events = response.json()
            
            # Check quantity
            if len(events) >= 12:
                self.log_success("Events Quantity", f"Found {len(events)} events (requirement: 12+)")
            else:
                self.log_issue("Events Quantity", f"Only {len(events)} events found, expected 12+")
            
            # Check for Paraguay-specific events mentioned in requirements
            expected_events = ["NASA Space Apps", "Iguassu Valley", "Design Week Asunción"]
            paraguay_events = 0
            organizers = set()
            
            for event in events:
                title = event.get('title', '').lower()
                organizer = event.get('organizer', '')
                location = event.get('location', '').lower()
                
                organizers.add(organizer)
                
                # Check for Paraguay-related content
                if 'paraguay' in location or 'asunción' in location or 'ciudad del este' in location:
                    paraguay_events += 1
                
                # Check for expected events
                for expected in expected_events:
                    if expected.lower() in title or expected.lower() in organizer.lower():
                        self.log_success("Event Content", f"Found expected event: {expected}")
                
                # Check required fields
                required_fields = ['title', 'description', 'organizer', 'url', 'event_date', 'location']
                missing_fields = [field for field in required_fields if not event.get(field)]
                if missing_fields:
                    self.log_issue("Event Data", f"Event '{event.get('title', 'Unknown')}' missing: {missing_fields}")
            
            if paraguay_events > 0:
                self.log_success("Paraguay Events", f"Found {paraguay_events} Paraguay-related events")
            else:
                self.log_issue("Paraguay Events", "No Paraguay-specific events found")
            
            return len(events) >= 12
            
        except Exception as e:
            self.log_issue("Events API", f"Failed to fetch events: {str(e)}")
            return False

    def verify_jobs_content(self):
        """Verify job vacancies content quality and quantity"""
        print("\n" + "="*60)
        print("🔍 VERIFYING JOB VACANCIES CONTENT")
        print("="*60)
        
        try:
            response = requests.get(f"{self.base_url}/jobs")
            jobs = response.json()
            
            # Check quantity
            if len(jobs) >= 6:
                self.log_success("Jobs Quantity", f"Found {len(jobs)} jobs (requirement: 6+)")
            else:
                self.log_issue("Jobs Quantity", f"Only {len(jobs)} jobs found, expected 6+")
            
            # Check for real companies mentioned in requirements
            expected_companies = ["Tigo", "Banco Continental", "Copetrol"]
            real_apply_urls = 0
            companies = set()
            
            for job in jobs:
                company_name = job.get('company_name', '')
                apply_url = job.get('apply_url', '')
                
                companies.add(company_name)
                
                # Check for real apply URLs (not fake/placeholder)
                if apply_url and apply_url.startswith('http') and not any(fake in apply_url.lower() for fake in ['example.com', 'placeholder', 'fake', 'test']):
                    real_apply_urls += 1
                    self.log_success("Job URLs", f"Real apply URL found for {company_name}: {apply_url}")
                elif apply_url:
                    self.log_issue("Job URLs", f"Suspicious apply URL for {company_name}: {apply_url}")
                else:
                    self.log_issue("Job URLs", f"Missing apply URL for {company_name}")
                
                # Check for expected companies
                for expected in expected_companies:
                    if expected.lower() in company_name.lower():
                        self.log_success("Job Companies", f"Found expected company: {expected}")
                
                # Check required fields
                required_fields = ['title', 'company_name', 'description', 'modality', 'job_type', 'apply_url']
                missing_fields = [field for field in required_fields if not job.get(field)]
                if missing_fields:
                    self.log_issue("Job Data", f"Job '{job.get('title', 'Unknown')}' missing: {missing_fields}")
            
            if real_apply_urls >= len(jobs) * 0.8:  # At least 80% should have real URLs
                self.log_success("Job URLs Quality", f"{real_apply_urls}/{len(jobs)} jobs have real apply URLs")
            else:
                self.log_issue("Job URLs Quality", f"Only {real_apply_urls}/{len(jobs)} jobs have real apply URLs")
            
            print(f"   Companies found: {', '.join(sorted(companies))}")
            
            return len(jobs) >= 6
            
        except Exception as e:
            self.log_issue("Jobs API", f"Failed to fetch jobs: {str(e)}")
            return False

    def verify_filters_functionality(self):
        """Verify that filters are working properly"""
        print("\n" + "="*60)
        print("🔍 VERIFYING FILTERS FUNCTIONALITY")
        print("="*60)
        
        # Test course category filters
        try:
            all_courses = requests.get(f"{self.base_url}/courses").json()
            if all_courses:
                # Get unique categories
                categories = list(set(course.get('category') for course in all_courses if course.get('category')))
                
                for category in categories[:3]:  # Test first 3 categories
                    filtered = requests.get(f"{self.base_url}/courses?category={category}").json()
                    if all(course.get('category') == category for course in filtered):
                        self.log_success("Course Filters", f"Category filter '{category}' working correctly")
                    else:
                        self.log_issue("Course Filters", f"Category filter '{category}' not working properly")
        except Exception as e:
            self.log_issue("Course Filters", f"Error testing filters: {str(e)}")
        
        # Test job modality filters
        try:
            all_jobs = requests.get(f"{self.base_url}/jobs").json()
            if all_jobs:
                modalities = list(set(job.get('modality') for job in all_jobs if job.get('modality')))
                
                for modality in modalities:
                    filtered = requests.get(f"{self.base_url}/jobs?modality={modality}").json()
                    if all(job.get('modality') == modality for job in filtered):
                        self.log_success("Job Filters", f"Modality filter '{modality}' working correctly")
                    else:
                        self.log_issue("Job Filters", f"Modality filter '{modality}' not working properly")
        except Exception as e:
            self.log_issue("Job Filters", f"Error testing job filters: {str(e)}")

    def test_saved_items_functionality(self):
        """Test saved items endpoints (without authentication)"""
        print("\n" + "="*60)
        print("🔍 VERIFYING SAVED ITEMS ENDPOINTS")
        print("="*60)
        
        # Test saved items endpoint (should require auth)
        try:
            response = requests.get(f"{self.base_url}/saved-items")
            if response.status_code == 401:
                self.log_success("Saved Items Security", "Saved items endpoint properly requires authentication")
            else:
                self.log_issue("Saved Items Security", f"Saved items endpoint returned {response.status_code}, expected 401")
        except Exception as e:
            self.log_issue("Saved Items API", f"Error testing saved items: {str(e)}")
        
        # Test save item endpoint (should require auth)
        try:
            response = requests.post(f"{self.base_url}/saved-items", json={"item_id": "test", "item_type": "course"})
            if response.status_code == 401:
                self.log_success("Save Item Security", "Save item endpoint properly requires authentication")
            else:
                self.log_issue("Save Item Security", f"Save item endpoint returned {response.status_code}, expected 401")
        except Exception as e:
            self.log_issue("Save Item API", f"Error testing save item: {str(e)}")

def main():
    print("🔍 Starting TechHub UPE Content Verification")
    print("="*70)
    
    tester = ContentVerificationTester()
    
    # Run all content verification tests
    courses_ok = tester.verify_courses_content()
    events_ok = tester.verify_events_content()
    jobs_ok = tester.verify_jobs_content()
    tester.verify_filters_functionality()
    tester.test_saved_items_functionality()
    
    # Print final summary
    print("\n" + "="*70)
    print("📊 CONTENT VERIFICATION SUMMARY")
    print("="*70)
    
    print(f"\n✅ SUCCESSES ({len(tester.successes)}):")
    for success in tester.successes:
        print(f"   {success}")
    
    if tester.issues:
        print(f"\n❌ ISSUES FOUND ({len(tester.issues)}):")
        for issue in tester.issues:
            print(f"   {issue}")
    else:
        print(f"\n🎉 NO ISSUES FOUND!")
    
    # Overall assessment
    critical_issues = [issue for issue in tester.issues if any(word in issue.lower() for word in ['quantity', 'missing', 'failed'])]
    
    if not critical_issues:
        print(f"\n🎉 OVERALL ASSESSMENT: EXCELLENT")
        print("   All content requirements appear to be met!")
        return 0
    else:
        print(f"\n⚠️  OVERALL ASSESSMENT: NEEDS ATTENTION")
        print(f"   {len(critical_issues)} critical issues found")
        return 1

if __name__ == "__main__":
    exit(main())