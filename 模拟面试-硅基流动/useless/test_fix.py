import unittest
from unittest.mock import MagicMock, patch
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dify_assistant import DifyAssistant
from backend.models.interview import InterviewManager
from backend.app import app


class TestInterviewSystem(unittest.TestCase):
    def setUp(self):
        self.assistant = DifyAssistant()
        self.interview_manager = InterviewManager("test_interview_system.db")
        # Initialize DB
        self.interview_manager.init_database()

        # Clean up old PDFs
        if not os.path.exists("面试记录"):
            os.makedirs("面试记录")

    def tearDown(self):
        # Clean up test DB
        if os.path.exists("test_interview_system.db"):
            try:
                os.remove("test_interview_system.db")
            except:
                pass

    @patch("requests.post")
    def test_full_flow_and_admin(self, mock_post):
        print("\n🚀 Starting Full Flow Test...")

        # Manual Patching of the global interview_manager in admin_routes
        import backend.routes.admin_routes

        original_manager = backend.routes.admin_routes.interview_manager
        backend.routes.admin_routes.interview_manager = self.interview_manager

        # Restore original manager after test
        def restore_manager():
            backend.routes.admin_routes.interview_manager = original_manager

        self.addCleanup(restore_manager)

        # Mock Responses
        responses = [
            # 1. Opening (Should NOT count as Q1)
            {
                "answer": "您好！欢迎参加本次 Java 开发工程师岗位的面试。下面我们开始。请简要介绍一下你自己。",
                "conversation_id": "conv_1",
            },
            # 2. Q1
            {"answer": "好的。第一个问题：请解释一下Java的多态性。", "conversation_id": "conv_1"},
            # 3. Q2
            {"answer": "不错。第二个问题：什么是Spring Boot？", "conversation_id": "conv_1"},
            # 4. Q3
            {"answer": "很好。第三个问题：介绍一下MySQL索引。", "conversation_id": "conv_1"},
            # 5. Q4
            {"answer": "继续。第四个问题：Redis有哪些数据类型？", "conversation_id": "conv_1"},
            # 6. Q5
            {"answer": "最后一个问题。第五个问题：如何处理高并发？", "conversation_id": "conv_1"},
            # 7. End
            {
                "answer": "面试结束。综合评估：通过。",
                "json_data": {"isPassed": "好", "final_evaluation": "优秀"},
                "conversation_id": "conv_1",
            },
        ]

        # Setup Mock
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: responses[0]),
            MagicMock(status_code=200, json=lambda: responses[1]),
            MagicMock(status_code=200, json=lambda: responses[2]),
            MagicMock(status_code=200, json=lambda: responses[3]),
            MagicMock(status_code=200, json=lambda: responses[4]),
            MagicMock(status_code=200, json=lambda: responses[5]),
            MagicMock(status_code=200, json=lambda: responses[6]),
        ]

        # 1. Start Interview
        res1 = self.assistant.send_message("Java Interview")
        print(
            f"Step 1 (Opening): Q_Count={self.assistant.question_count}, Interviewing={self.assistant.is_interviewing}"
        )
        self.assertTrue(self.assistant.is_interviewing)
        self.assertEqual(
            self.assistant.question_count,
            0,
            "Opening should NOT increment question count",
        )

        # 2. User answers intro -> AI asks Q1
        res2 = self.assistant.send_message("I am a developer.")
        print(f"Step 2 (Q1): Q_Count={self.assistant.question_count}")
        self.assertEqual(self.assistant.question_count, 1)

        # 3. User answers Q1 -> AI asks Q2
        res3 = self.assistant.send_message("Polymorphism is...")
        print(f"Step 3 (Q2): Q_Count={self.assistant.question_count}")
        self.assertEqual(self.assistant.question_count, 2)

        # 4. User answers Q2 -> AI asks Q3
        self.assistant.send_message("Spring Boot is...")
        print(f"Step 4 (Q3): Q_Count={self.assistant.question_count}")
        # 5. User answers Q3 -> AI asks Q4
        self.assistant.send_message("Index is...")
        print(f"Step 5 (Q4): Q_Count={self.assistant.question_count}")
        # 6. User answers Q4 -> AI asks Q5
        self.assistant.send_message("Redis types...")
        print(f"Step 6 (Q5): Q_Count={self.assistant.question_count}")
        self.assertEqual(self.assistant.question_count, 5)

        # 7. User answers Q5 -> AI ends interview
        res_end = self.assistant.send_message("Concurrency handling...")
        print(f"Step 7 (End): Interviewing={self.assistant.is_interviewing}")
        self.assertFalse(self.assistant.is_interviewing)

        # 8. Simulate Saving
        interview_data = {
            "job_name": "Java Engineer",
            "qa_pairs": [
                {
                    "question": "Q1",
                    "answer": "A1",
                    "evaluation": "Good",
                    "is_passed": True,
                },
                {
                    "question": "Q2",
                    "answer": "A2",
                    "evaluation": "Good",
                    "is_passed": True,
                },
                {
                    "question": "Q3",
                    "answer": "A3",
                    "evaluation": "Good",
                    "is_passed": True,
                },
                {
                    "question": "Q4",
                    "answer": "A4",
                    "evaluation": "Good",
                    "is_passed": True,
                },
                {
                    "question": "Q5",
                    "answer": "A5",
                    "evaluation": "Good",
                    "is_passed": True,
                },
            ],
            "total_questions": 5,
            "passed_questions": 5,
            "pass_rate": "100%",
            "final_evaluation": "Excellent",
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        pdf_path = self.assistant.save_interview_results(interview_data)
        print(f"PDF Generated at: {pdf_path}")
        self.assertTrue(os.path.exists(pdf_path))

        # 9. Verify DB Storage
        self.interview_manager.create_interview("conv_1", "Java Engineer")
        for qa in interview_data["qa_pairs"]:
            self.interview_manager.save_qa_record(
                "conv_1",
                qa["question"],
                qa["answer"],
                qa["evaluation"],
                qa["is_passed"],
            )
        self.interview_manager.finish_interview("conv_1", "Excellent", pdf_path)

        interview_rec = self.interview_manager.get_interview_by_session("conv_1")
        self.assertIsNotNone(interview_rec)

        # 10. Test Admin Routes
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["admin_logged_in"] = True

            # Test Get Details
            interview_id = interview_rec["id"]
            resp = client.get(f"/api/interview-details/{interview_id}")
            data = resp.get_json()
            print(f"Admin Details Response: {data}")
            self.assertTrue(data["success"])
            self.assertEqual(data["interview"]["job_name"], "Java Engineer")

            # Test Download PDF
            resp_pdf = client.get(f"/api/interview-pdf/{interview_id}")
            if resp_pdf.mimetype == "application/json":
                print(f"Admin PDF Download Failed: {resp_pdf.get_json()}")
            self.assertEqual(resp_pdf.status_code, 200)
            self.assertEqual(resp_pdf.mimetype, "application/pdf")
            print("Admin PDF Download Successful")


if __name__ == "__main__":
    unittest.main()
