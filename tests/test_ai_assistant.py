import json
import unittest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
from src.ai_assistant import build_context, context_id, ask_openai
from src.risk_engine import assess_deals
from test_analytics import example, AS_OF


class AssistantTests(unittest.TestCase):
    def setUp(self):
        self.data = assess_deals(example(), AS_OF)
        self.context = build_context(self.data, AS_OF, 30)

    def test_context_is_aggregate_only_and_reconciles(self):
        encoded = json.dumps(self.context)
        self.assertNotIn('deal_id', encoded)
        self.assertNotIn('sales_rep', encoded)
        self.assertEqual(self.context['kpis']['revenue_at_risk'], 1100)
        self.assertEqual(sum(x['revenue_at_risk'] for x in self.context['groups']['stage']['rows']), 1100)

    def test_empty_and_missing_optional(self):
        c = build_context(self.data.iloc[:0].drop(columns='delay_reason'), AS_OF, 30)
        self.assertIsNone(c['groups']['delay_reason'])
        self.assertIsNone(c['kpis']['win_rate'])
        self.assertEqual(c['groups']['stage']['rows'], [])

    def test_context_change_invalidates_conversation(self):
        a = context_id(self.context, 'sourceA')
        self.assertNotEqual(a, context_id(self.context, 'sourceB'))
        self.assertNotEqual(a, context_id(dict(self.context, stalled_threshold_days=60), 'sourceA'))

    @patch('src.ai_assistant.http.client.HTTPSConnection')
    def test_request_contract_and_bounded_history(self, constructor):
        connection = constructor.return_value
        response = connection.getresponse.return_value
        response.status = 200
        response.read.return_value = json.dumps({'status':'completed', 'output':[{'type':'message','content':[{'type':'output_text','text':'Evidence-based answer'}]}]}).encode()
        history = [{'role':'user','content':'prior'}] * 20
        self.assertEqual(ask_openai('test-key','Explain risk',self.context,history),'Evidence-based answer')
        payload = json.loads(connection.request.call_args.kwargs['body'])
        self.assertFalse(payload['store'])
        self.assertEqual(payload['max_output_tokens'],900)
        self.assertEqual(len(payload['input']),8)
        self.assertNotIn('tools',payload)
        connection.close.assert_called_once()

    @patch('src.ai_assistant.http.client.HTTPSConnection')
    def test_errors_hide_provider_details(self, constructor):
        response = constructor.return_value.getresponse.return_value
        response.status = 401
        with self.assertRaisesRegex(ValueError,'key was not accepted'):
            ask_openai('test-key','Question',self.context,[])
        response.read.assert_not_called()
        constructor.return_value.request.side_effect = OSError('secret-in-error')
        with self.assertRaisesRegex(ValueError,'connection could not finish'):
            ask_openai('test-key','Question',self.context,[])

    @patch('src.ai_assistant.http.client.HTTPSConnection')
    def test_invalid_input_never_connects(self, constructor):
        for key, question in [('', 'Question'), ('test-key', ''), ('test-key', 'x'*1201), ('bad\nkey', 'Question')]:
            with self.assertRaises(ValueError):
                ask_openai(key,question,self.context,[])
        constructor.assert_not_called()

    @patch('src.ai_assistant.http.client.HTTPSConnection')
    def test_incomplete_response_is_not_presented_as_answer(self, constructor):
        response = constructor.return_value.getresponse.return_value
        response.status = 200
        response.read.return_value = b'{"status":"incomplete","output":[]}'
        with self.assertRaisesRegex(ValueError,'incomplete'):
            ask_openai('test-key','Question',self.context,[])

    def test_ui_consent_reset_and_success_without_network(self):
        app = AppTest.from_file('app.py', default_timeout=30).run()
        self.assertEqual(app.tabs[4].label,'Ask AI')
        app.radio[0].set_value('Try sample data').run()
        next(b for b in app.button if b.label=='Check data').click().run()
        self.assertTrue(next(b for b in app.button if b.label=='Ask AI').disabled)
        app.text_input(key='ai_key').set_value('test-key').run()
        app.checkbox(key='ai_consent').check().run()
        app.text_area(key='ai_question').set_value('Explain exposure').run()
        with patch('src.assistant_view.ask_openai', return_value='Test response based on supplied evidence.') as api:
            next(b for b in app.button if b.label=='Ask AI').click().run()
            api.assert_called_once()
        self.assertEqual(len(app.session_state['ai_history']),2)
        next(x for x in app.number_input if 'Stalled after' in x.label).set_value(60).run()
        self.assertEqual(app.session_state['ai_history'],[])
        self.assertFalse(app.checkbox(key='ai_consent').value)
        next(b for b in app.button if b.label=='Disconnect and clear conversation').click().run()
        self.assertEqual(app.text_input(key='ai_key').value,'')
        self.assertFalse(app.exception)
