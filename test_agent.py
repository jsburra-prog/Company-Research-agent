import unittest
from unittest.mock import patch, MagicMock
from agent_logic import validate_company, find_careers_page
from bs4 import BeautifulSoup

class TestCompanyResearchAgent(unittest.TestCase):

    def test_find_careers_page(self):
        html = '<html><body><a href="/about">About</a><a href="/careers">Careers</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        url = find_careers_page(soup, "http://example.com")
        self.assertEqual(url, "http://example.com/careers")

    def test_find_careers_page_complex(self):
        html = '<html><body><a href="/jobs">We are hiring!</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        url = find_careers_page(soup, "http://example.com")
        self.assertEqual(url, "http://example.com/jobs")

    @patch('agent_logic.get_page_content')
    def test_validate_company_success(self, mock_get_content):
        # Mock Homepage
        mock_get_content.side_effect = [
            """
            <html><body>
                <p>We are a strategy consulting firm engaged in digital transformation.</p>
                <p>We focus on business outcomes and ROI for our partners.</p>
                <a href="/careers">Careers</a>
            </body></html>
            """,
            # Mock Careers Page
            """
            <html><body>
                <p>Open roles:</p>
                <ul>
                    <li>Principal Consultant</li>
                    <li>Engagement Manager</li>
                    <li>Strategy Lead</li>
                </ul>
            </body></html>
            """
        ]

        result = validate_company("Good Firm", "http://goodfirm.com")
        self.assertIsNotNone(result)
        self.assertEqual(result['Company'], "Good Firm")
        self.assertIn("Outcome-based language detected", result['Why It Fits'])

    @patch('agent_logic.get_page_content')
    def test_validate_company_failure_body_shop(self, mock_get_content):
         # Mock Homepage
        mock_get_content.side_effect = [
            """
            <html><body>
                <p>We provide staff augmentation and 100+ engineers for your project.</p>
                <p>Hiring engineers is hard, let us help.</p>
                <a href="/careers">Join Us</a>
            </body></html>
            """,
            # Mock Careers Page
            """
            <html><body>
                <p>Open roles:</p>
                <ul>
                    <li>Java Developer</li>
                    <li>React Developer</li>
                    <li>QA Engineer</li>
                    <li>Another Dev</li>
                    <li>Another Dev</li>
                </ul>
            </body></html>
            """
        ]

        result = validate_company("Body Shop", "http://bodyshop.com")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
