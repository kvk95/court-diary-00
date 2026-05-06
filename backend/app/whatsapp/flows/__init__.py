# app/whatsapp/flows/__init__.py

from app.whatsapp.flow_registry import register_flow

from app.whatsapp.flows.add_case import start_add_case, handle_add_case
from app.whatsapp.flows.search_case import start_search_case, handle_search_case
from app.whatsapp.flows.add_hearing import start_add_hearing, handle_add_hearing
from app.whatsapp.flows.add_note import start_add_note, handle_add_note
from app.whatsapp.flows.update_case_status import start_update_case_status, handle_update_case_status

register_flow("add_case", start=start_add_case, handler=handle_add_case)
register_flow("search_case", start=start_search_case, handler=handle_search_case)
register_flow("add_hearing", start=start_add_hearing, handler=handle_add_hearing)
register_flow("add_note", start=start_add_note, handler=handle_add_note)
register_flow("update_case_status", start=start_update_case_status, handler=handle_update_case_status)