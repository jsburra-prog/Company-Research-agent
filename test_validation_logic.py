
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

    @patch('agent_logic.get_page_content')
    def test_validate_company_partner_keywords(self, mock_get_content):
        # Mock Homepage with "Partner" and "Ecosystem" keywords
        mock_get_content.side_effect = [
            """
            <html><body>
                <p>We are a trusted partner in the digital ecosystem.</p>
                <p>Building strong alliances.</p>
            </body></html>
            """,
            None # No careers page for this test or it returns None
        ]

        result = validate_company("Partner Firm", "http://partnerfirm.com")
        self.assertIsNotNone(result)
        self.assertEqual(result['Company'], "Partner Firm")
        self.assertIn("Partner/Ecosystem language detected", result['Why It Fits'])

    @patch('agent_logic.get_page_content')
    def test_validate_company_consulting_roles(self, mock_get_content):
        # Mock Homepage (neutral)
        mock_get_content.side_effect = [
            """
            <html><body>
                <p>We build software.</p>
                <a href="/careers">Careers</a>
            </body></html>
            """,
            # Mock Careers Page with Consulting Roles
            """
            <html><body>
                <p>Open roles:</p>
                <ul>
                    <li>Senior Consultant</li>
                    <li>Strategy Lead</li>
                </ul>
            </body></html>
            """
        ]

        result = validate_company("Consulting Firm", "http://consultingfirm.com")
        self.assertIsNotNone(result)
        self.assertEqual(result['Company'], "Consulting Firm")
        self.assertIn("Hiring consulting roles", result['Why It Fits'])

    @patch('agent_logic.get_page_content')
    def test_validate_company_outcome_language(self, mock_get_content):
         # Mock Homepage with Outcome Language
        mock_get_content.side_effect = [
            """
            <html><body>
                <p>We drive business outcomes and ROI.</p>
            </body></html>
            """,
            None
        ]
        result = validate_company("Outcome Firm", "http://outcomefirm.com")
        self.assertIsNotNone(result)
        self.assertIn("Outcome-based language detected", result['Why It Fits'])


if __name__ == '__main__':
    unittest.main()
