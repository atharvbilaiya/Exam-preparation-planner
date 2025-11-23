"""
Student Study Planner - Exam Preparation Module
A comprehensive exam preparation system built with pure Python
Author: [Your Friend's Name]
Course: Introduction to Problem Solving & Programming
"""

import datetime
import os

class Exam:
    """
    Represents an exam with all preparation details
    """
    def __init__(self, subject, exam_date, topics, priority="Medium", current_progress=0):
        self.subject = subject
        self.exam_date = exam_date
        self.topics = topics  # List of topics to study
        self.priority = priority  # High, Medium, Low
        self.current_progress = current_progress  # Percentage 0-100
        self.created_date = datetime.date.today()
    
    def get_days_remaining(self):
        """Calculate days remaining until exam"""
        today = datetime.date.today()
        return (self.exam_date - today).days
    
    def get_study_recommendation(self):
        """Generate study recommendation based on days remaining"""
        days_remaining = self.get_days_remaining()
        topics_remaining = len([t for t in self.topics if not t['completed']])
        
        if days_remaining <= 0:
            return "Exam is today or has passed!"
        
        if topics_remaining == 0:
            return "All topics completed! Focus on revision."
        
        daily_topics = max(1, topics_remaining // days_remaining)
        return f"Study {daily_topics} topic(s) per day to complete on time."
    
    def update_progress(self):
        """Calculate current progress percentage"""
        if not self.topics:
            self.current_progress = 0
            return
        
        completed_topics = len([t for t in self.topics if t['completed']])
        total_topics = len(self.topics)
        self.current_progress = (completed_topics / total_topics) * 100
    
    def to_dict(self):
        """Convert exam to dictionary for storage"""
        return {
            'subject': self.subject,
            'exam_date': self.exam_date.strftime("%Y-%m-%d"),
            'topics': self.topics,
            'priority': self.priority,
            'current_progress': self.current_progress,
            'created_date': self.created_date.strftime("%Y-%m-%d")
        }

class StudyPlanGenerator:
    """
    Generates and manages study plans for exams
    """
    def __init__(self, data_file="exam_data.txt"):
        self.data_file = data_file
        self.exams = []
        self.subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology', 
                        'Computer Science', 'English', 'History', 'Geography']
        self.load_data()
    
    def save_data(self):
        """Save exams data to file"""
        try:
            with open(self.data_file, 'w') as f:
                f.write("[EXAMS]\n")
                for exam in self.exams:
                    exam_data = exam.to_dict()
                    # Save exam basic info
                    f.write(f"EXAM_START\n")
                    f.write(f"subject:{exam_data['subject']}\n")
                    f.write(f"exam_date:{exam_data['exam_date']}\n")
                    f.write(f"priority:{exam_data['priority']}\n")
                    f.write(f"current_progress:{exam_data['current_progress']}\n")
                    f.write(f"created_date:{exam_data['created_date']}\n")
                    
                    # Save topics
                    f.write("topics_start\n")
                    for topic in exam_data['topics']:
                        completed = "1" if topic['completed'] else "0"
                        f.write(f"topic:{topic['name']},{completed},{topic['importance']}\n")
                    f.write("topics_end\n")
                    f.write(f"EXAM_END\n")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_data(self):
        """Load exams data from file"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r') as f:
                lines = f.readlines()
                current_exam = None
                reading_topics = False
                
                for line in lines:
                    line = line.strip()
                    
                    if line == "EXAM_START":
                        current_exam = {}
                    elif line == "EXAM_END" and current_exam:
                        self._create_exam_from_data(current_exam)
                        current_exam = None
                    elif line == "topics_start":
                        reading_topics = True
                        current_exam['topics'] = []
                    elif line == "topics_end":
                        reading_topics = False
                    elif current_exam is not None:
                        if reading_topics and line.startswith("topic:"):
                            topic_data = line[6:].split(',')
                            if len(topic_data) == 3:
                                topic = {
                                    'name': topic_data[0],
                                    'completed': topic_data[1] == "1",
                                    'importance': topic_data[2]
                                }
                                current_exam['topics'].append(topic)
                        else:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                key, value = parts
                                current_exam[key] = value
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def _create_exam_from_data(self, exam_data):
        """Create Exam object from loaded data"""
        try:
            subject = exam_data.get('subject', '')
            exam_date = datetime.datetime.strptime(exam_data['exam_date'], "%Y-%m-%d").date()
            priority = exam_data.get('priority', 'Medium')
            current_progress = float(exam_data.get('current_progress', 0))
            topics = exam_data.get('topics', [])
            
            exam = Exam(subject, exam_date, topics, priority, current_progress)
            exam.created_date = datetime.datetime.strptime(exam_data['created_date'], "%Y-%m-%d").date()
            self.exams.append(exam)
        except Exception as e:
            print(f"Error creating exam: {e}")
    
    def add_exam(self, subject, exam_date, topics_list, priority="Medium"):
        """Add a new exam to track"""
        if subject not in self.subjects:
            return False, "Invalid subject"
        
        try:
            # Convert topics list to proper format
            topics = []
            for topic_name in topics_list:
                topics.append({
                    'name': topic_name,
                    'completed': False,
                    'importance': 'High'  # Default importance
                })
            
            exam = Exam(subject, exam_date, topics, priority)
            self.exams.append(exam)
            self.save_data()
            return True, f"Exam for {subject} added successfully!"
        except Exception as e:
            return False, f"Error adding exam: {e}"
    
    def get_upcoming_exams(self, days=30):
        """Get exams happening in the next specified days"""
        today = datetime.date.today()
        upcoming = []
        
        for exam in self.exams:
            days_remaining = exam.get_days_remaining()
            if 0 <= days_remaining <= days:
                upcoming.append(exam)
        
        # Sort by days remaining
        upcoming.sort(key=lambda x: x.get_days_remaining())
        return upcoming
    
    def generate_study_schedule(self, exam, study_hours_per_day=2):
        """Generate a detailed study schedule for an exam"""
        days_remaining = exam.get_days_remaining()
        if days_remaining <= 0:
            return "Exam has already passed or is today."
        
        incomplete_topics = [t for t in exam.topics if not t['completed']]
        
        if not incomplete_topics:
            return "All topics completed! Focus on revision."
        
        schedule = []
        schedule.append(f"Study Schedule for {exam.subject} ({days_remaining} days remaining)")
        schedule.append("=" * 50)
        
        # Calculate topics per day
        topics_per_day = max(1, len(incomplete_topics) // days_remaining)
        
        current_day = 1
        topics_scheduled = 0
        
        while topics_scheduled < len(incomplete_topics) and current_day <= days_remaining:
            day_topics = incomplete_topics[topics_scheduled:topics_scheduled + topics_per_day]
            topics_names = [t['name'] for t in day_topics]
            schedule.append(f"Day {current_day}: {', '.join(topics_names)}")
            
            topics_scheduled += len(day_topics)
            current_day += 1
        
        # Add revision days if there's time
        if current_day <= days_remaining:
            revision_days = days_remaining - current_day + 1
            schedule.append(f"Last {revision_days} day(s): Revision and practice tests")
        
        return "\n".join(schedule)
    
    def mark_topic_completed(self, exam_index, topic_index):
        """Mark a topic as completed and update progress"""
        if 0 <= exam_index < len(self.exams):
            exam = self.exams[exam_index]
            if 0 <= topic_index < len(exam.topics):
                exam.topics[topic_index]['completed'] = True
                exam.update_progress()
                self.save_data()
                return True, "Topic marked as completed!"
        return False, "Invalid exam or topic index"
    
    def get_study_priority(self):
        """Get exams sorted by study priority"""
        priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
        
        def exam_priority(exam):
            days_remaining = exam.get_days_remaining()
            priority_score = priority_order.get(exam.priority, 1)
            
            # Higher priority for exams with fewer days remaining
            if days_remaining <= 7:
                urgency_multiplier = 3
            elif days_remaining <= 14:
                urgency_multiplier = 2
            else:
                urgency_multiplier = 1
            
            return (priority_score * urgency_multiplier, -days_remaining)
        
        return sorted(self.exams, key=exam_priority, reverse=True)
    
    def get_study_analytics(self):
        """Generate study analytics and insights"""
        if not self.exams:
            return "No exams to analyze. Add some exams to get started!"
        
        total_exams = len(self.exams)
        upcoming_exams = self.get_upcoming_exams(30)
        total_upcoming = len(upcoming_exams)
        
        analytics = []
        analytics.append("STUDY ANALYTICS & INSIGHTS")
        analytics.append("=" * 40)
        analytics.append(f"Total exams tracked: {total_exams}")
        analytics.append(f"Exams in next 30 days: {total_upcoming}")
        analytics.append("")
        
        if upcoming_exams:
            analytics.append("UPCOMING EXAMS PRIORITY:")
            for i, exam in enumerate(self.get_study_priority()[:5], 1):
                days = exam.get_days_remaining()
                analytics.append(f"{i}. {exam.subject} - {days} days left - {exam.current_progress:.1f}% complete")
        
        # Overall progress
        if self.exams:
            avg_progress = sum(exam.current_progress for exam in self.exams) / len(self.exams)
            analytics.append(f"\nAverage completion: {avg_progress:.1f}%")
            
            if avg_progress < 30:
                analytics.append("💡 Recommendation: Increase study pace!")
            elif avg_progress < 70:
                analytics.append("💡 Recommendation: Good progress, keep consistent!")
            else:
                analytics.append("💡 Recommendation: Excellent progress! Focus on revision.")
        
        return "\n".join(analytics)

class ExamPlannerInterface:
    """
    User interface for the exam planner
    """
    def __init__(self):
        self.planner = StudyPlanGenerator()
    
    def display_main_menu(self):
        """Display the main menu"""
        print("\n" + "="*60)
        print("           EXAM PREPARATION PLANNER")
        print("="*60)
        print("1. Add New Exam")
        print("2. View Upcoming Exams")
        print("3. Generate Study Schedule")
        print("4. Mark Topic Completed")
        print("5. Study Analytics & Insights")
        print("6. Study Priority List")
        print("7. View All Exams")
        print("8. Exit")
        print("="*60)
    
    def add_new_exam(self):
        """Handle adding a new exam"""
        print("\n--- Add New Exam ---")
        
        # Display available subjects
        print("Available Subjects:", ", ".join(self.planner.subjects))
        subject = input("Enter subject: ").strip()
        if subject not in self.planner.subjects:
            print("Invalid subject! Please choose from the list.")
            return
        
        # Get exam date
        try:
            date_str = input("Enter exam date (YYYY-MM-DD): ").strip()
            exam_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if exam_date < datetime.date.today():
                print("Exam date cannot be in the past!")
                return
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD.")
            return
        
        # Get topics
        print("Enter topics (one per line, leave empty to finish):")
        topics = []
        while True:
            topic = input("Topic: ").strip()
            if not topic:
                break
            topics.append(topic)
        
        if not topics:
            print("At least one topic is required!")
            return
        
        # Get priority
        priority = input("Enter priority (High/Medium/Low) [Medium]: ").strip()
        if priority not in ['High', 'Medium', 'Low']:
            priority = "Medium"
        
        success, message = self.planner.add_exam(subject, exam_date, topics, priority)
        print(message)
    
    def view_upcoming_exams(self):
        """Display upcoming exams"""
        print("\n--- Upcoming Exams (Next 30 Days) ---")
        upcoming = self.planner.get_upcoming_exams(30)
        
        if not upcoming:
            print("No upcoming exams in the next 30 days.")
            return
        
        for i, exam in enumerate(upcoming, 1):
            days = exam.get_days_remaining()
            print(f"{i}. {exam.subject} - {exam.exam_date} ({days} days left)")
            print(f"   Progress: {exam.current_progress:.1f}% | Priority: {exam.priority}")
            print(f"   Recommendation: {exam.get_study_recommendation()}")
            print()
    
    def generate_study_schedule(self):
        """Generate and display study schedule"""
        exams = self.planner.exams
        if not exams:
            print("No exams available. Add an exam first.")
            return
        
        print("\n--- Generate Study Schedule ---")
        for i, exam in enumerate(exams, 1):
            print(f"{i}. {exam.subject} - {exam.exam_date}")
        
        try:
            choice = int(input("Select exam number: ")) - 1
            if 0 <= choice < len(exams):
                schedule = self.planner.generate_study_schedule(exams[choice])
                print(f"\n{schedule}")
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
    
    def mark_topic_completed(self):
        """Mark a topic as completed"""
        exams = self.planner.exams
        if not exams:
            print("No exams available. Add an exam first.")
            return
        
        print("\n--- Mark Topic Completed ---")
        for i, exam in enumerate(exams, 1):
            print(f"{i}. {exam.subject}")
        
        try:
            exam_choice = int(input("Select exam number: ")) - 1
            if not (0 <= exam_choice < len(exams)):
                print("Invalid exam selection!")
                return
            
            exam = exams[exam_choice]
            print(f"\nTopics for {exam.subject}:")
            for j, topic in enumerate(exam.topics, 1):
                status = "✓" if topic['completed'] else "✗"
                print(f"{j}. [{status}] {topic['name']}")
            
            topic_choice = int(input("Select topic number to mark completed: ")) - 1
            success, message = self.planner.mark_topic_completed(exam_choice, topic_choice)
            print(message)
            
        except ValueError:
            print("Please enter valid numbers!")
    
    def show_study_analytics(self):
        """Display study analytics"""
        print("\n--- Study Analytics & Insights ---")
        analytics = self.planner.get_study_analytics()
        print(analytics)
    
    def show_priority_list(self):
        """Display study priority list"""
        print("\n--- Study Priority List ---")
        priority_exams = self.planner.get_study_priority()
        
        if not priority_exams:
            print("No exams to display.")
            return
        
        for i, exam in enumerate(priority_exams, 1):
            days = exam.get_days_remaining()
            print(f"{i}. {exam.subject} - {days} days left - {exam.priority} Priority")
            print(f"   Progress: {exam.current_progress:.1f}%")
            print(f"   {exam.get_study_recommendation()}")
            print()
    
    def view_all_exams(self):
        """Display all exams"""
        print("\n--- All Tracked Exams ---")
        if not self.planner.exams:
            print("No exams being tracked.")
            return
        
        for i, exam in enumerate(self.planner.exams, 1):
            days = exam.get_days_remaining()
            status = "UPCOMING" if days > 0 else "PASSED"
            print(f"{i}. {exam.subject} - {exam.exam_date} ({days} days - {status})")
            print(f"   Progress: {exam.current_progress:.1f}% | Topics: {len(exam.topics)}")
            completed = len([t for t in exam.topics if t['completed']])
            print(f"   Completed: {completed}/{len(exam.topics)} topics")
            print()
    
    def run(self):
        """Main application loop"""
        print("Welcome to Exam Preparation Planner!")
        print("Plan your studies effectively and ace your exams!")
        
        while True:
            self.display_main_menu()
            choice = input("Enter your choice (1-8): ").strip()
            
            try:
                if choice == '1':
                    self.add_new_exam()
                elif choice == '2':
                    self.view_upcoming_exams()
                elif choice == '3':
                    self.generate_study_schedule()
                elif choice == '4':
                    self.mark_topic_completed()
                elif choice == '5':
                    self.show_study_analytics()
                elif choice == '6':
                    self.show_priority_list()
                elif choice == '7':
                    self.view_all_exams()
                elif choice == '8':
                    print("Thank you for using Exam Preparation Planner!")
                    print("Good luck with your exams! 🎯")
                    break
                else:
                    print("Invalid choice! Please enter 1-8.")
            except KeyboardInterrupt:
                print("\n\nApplication interrupted. Saving data...")
                self.planner.save_data()
                break
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    """Main function to start the application"""
    try:
        app = ExamPlannerInterface()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
    except Exception as e:
        print(f"Fatal error: {e}")

if __name__ == "__main__":
    main()