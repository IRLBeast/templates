import os
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from .services.runner import run_pytest
import ibm_db
from dotenv import load_dotenv

load_dotenv()

def index(request):
    return render(request, "tests_manager/index.html")

def aiskr(request):
    return render(request, "tests_manager/aiskr.html")

def asubs(request):
    return render(request, "tests_manager/asubs.html")

def isip(request):
    return render(request, "tests_manager/isip.html")

def asbdb(request):
    return render(request, "tests_manager/asbdb.html")

def rinok(request):
    return render(request, "tests_manager/rinok.html")

def smp(request):
    return render(request, "tests_manager/smp.html")

def documents(request):
    return render(request, "tests_manager/documents.html")

def biss_table(request):
    return render(request, "tests_manager/biss_table.html")

def biss_mx(request):
    return render(request, "tests_manager/biss_mx.html")

def smp_table(request):
    return render(request, "tests_manager/smp_table.html")

ALLOWED_SCHEMAS = {
    "RTGX": "RTGX",
    "BIKL": "BIKL",
    "SKLI": "SKLI",
}


def get_schema(request, default="RTGX"):
    requested_schema = request.GET.get("schema", default)

    return ALLOWED_SCHEMAS.get(
        requested_schema,
        default
    )

def get_connection(db_type="main"):
    if db_type == "smp":
	database = os.getenv("SMP_DB_MAINFRAME_2B_NAME")
        host = os.getenv("SMP_DB_HOST")
        port = os.getenv("SMP_DB_PORT")
	user = os.getenv("DB_USER_SMP")
    else:
	database = os.getenv("DB_MAINFRAME_2B_NAME")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
	user = os.getenv("DB_USER_BISS")

    conn_str = (
        f"DATABASE={database};"
        f"HOSTNAME={host};"
        f"PORT={port};"
        "PROTOCOL=TCPIP;"
        f"UID={user};"
        f"PWD={os.getenv('DB_PASSWORD_BISS')};"
    )

    return ibm_db.connect(conn_str, "", "")

def get_messages(request, db_type="main", default_schema="RTGX"):

    schema = get_schema(request, default=default_schema)
    
    conn = get_connection(db_type)

    stmt = ibm_db.exec_immediate(
        conn,
        '''
        SELECT
            "IdMessageInMX",
            "IdMessageIn",
            "TmIn",
            "CdErrorIn",
            "BizSvc",
            "BizMsgIdr",
            "MsgDefIdr",
            "NrBankSender",
            "CdAuthSender",
            "NrBankReceiver",
            "CdAuthReceiver"
        FROM {schema}."MessageInMX"
        ORDER BY "TmIn" DESC
        FETCH FIRST 50 ROWS ONLY
        '''
    )

    headers = [
        ibm_db.field_name(stmt, i)
        for i in range(ibm_db.num_fields(stmt))
    ]

    rows = []

    while ibm_db.fetch_row(stmt):
        row = {}

        for i, h in enumerate(headers):
            value = ibm_db.result(stmt, i)

            if hasattr(value, "isoformat"):
                value = value.isoformat()

            row[h] = value

        rows.append(row)

    ibm_db.close(conn)

    return JsonResponse(rows, safe=False)


def get_smp_messages(request):
    return get_messages(
        request,
        db_type="smp",
        default_schema="BIKL"
    )


def get_message(request, message_id, db_type="main", default_schema="RTGX"):

    schema = get_schema(request, default=default_schema)

    conn = get_connection(db_type)

    sql = '''
        SELECT t1."MsgText"
        FROM {schema}."MessageGet" t1
        RIGHT JOIN {schema}."MessageInMX" t2 ON t1."IdMessageGet" = t2."IdMessageInMX"
        WHERE t2."IdMessageInMX" = ?
    '''

    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, message_id)
    ibm_db.execute(stmt)
    message = ""
    if ibm_db.fetch_row(stmt):
        message = ibm_db.result(stmt, 0)

    ibm_db.close(conn)

    return JsonResponse({
        "message": message
    })

def get_smp_message(request, message_id):
    return get_message(
        request,
        message_id,
        db_type="smp",
        default_schema="BIKL"
    )

def get_outgoing_messages(request, message_id, db_type="main", default_schema="RTGX"):

    schema = get_schema(request, default=default_schema)

    conn = get_connection(db_type)

    sql = """
    SELECT
        "IdMessageOutMX",
        CAST("TmOut" AS VARCHAR(26)) AS "TmOut",
        "NrBankSender",
        "CdAuthSender",
        "NrBankReceiver",
        "CdAuthReceiver",
        "BizSvc",
        "BizMsgIdr",
        "MsgDefIdr",
        "IdMessageInMX"
    FROM {schema}."MessageOutMX"
    WHERE "IdMessageInMX" = ?
    ORDER BY "TmOut" DESC
    """

    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, message_id)
    ibm_db.execute(stmt)

    num_cols = ibm_db.num_fields(stmt)
    headers = [ibm_db.field_name(stmt, i) for i in range(num_cols)]

    rows = []

    while ibm_db.fetch_row(stmt):
        row = {}

        for i, h in enumerate(headers):
            value = ibm_db.result(stmt, i)

            if hasattr(value, "isoformat"):
                value = value.isoformat()

            row[h] = value

        rows.append(row)

    ibm_db.close(conn)

    return JsonResponse(rows, safe=False)

def get_smp_outgoing_messages(request, message_id):
    return get_outgoing_messages(
        request,
        message_id,
        db_type="smp",
        default_schema="BIKL"
    )


def get_outgoing_message(request, message_id, db_type="main", default_schema="RTGX"):

    schema = get_schema(request, default=default_schema)

    conn = get_connection(db_type)

    sql = """
    SELECT "MsgText"
    FROM {schema}."MessageOutMX"
    WHERE "IdMessageOutMX" = ?
    """

    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, message_id)
    ibm_db.execute(stmt)

    message = ""

    if ibm_db.fetch_row(stmt):
        message = ibm_db.result(stmt, 0)

    ibm_db.close(conn)

    return JsonResponse({
        "message": message
    })

def get_smp_outgoing_message(request, message_id):
    return get_outgoing_message(
        request,
        message_id,
        db_type="smp",
        default_schema="BIKL"
    )

def get_messages_admin(request, db_type="main", default_schema="RTGX"):

    schema = get_schema(request, default=default_schema)

    conn = get_connection(db_type)

    stmt = ibm_db.exec_immediate(
        conn,
        '''
        SELECT
            "IdMsgSec",
            "IdMessageGet",
            "CdError",
            "ClassMsg",
            "TmCreate",
            "MsgText"
        FROM {schema}."MsgSecurityMX"
        ORDER BY "TmCreate" DESC
        '''
    )

    headers = [
        ibm_db.field_name(stmt, i)
        for i in range(ibm_db.num_fields(stmt))
    ]

    rows = []

    while ibm_db.fetch_row(stmt):
        row = {}

        for i, h in enumerate(headers):
            value = ibm_db.result(stmt, i)

            if hasattr(value, "isoformat"):
                value = value.isoformat()

            row[h] = value

        rows.append(row)

    ibm_db.close(conn)

    return JsonResponse(rows, safe=False)

def get_smp_messages_admin(request):
    return get_messages_admin(
        request,
        db_type="smp",
        default_schema="BIKL"
    )

def get_message_admin(request, message_id, db_type="main", default_schema="RTGX"):

    schema = get_schema(request, default=default_schema)

    conn = get_connection(db_type)

    sql = '''
        SELECT "MsgText"
        FROM {schema}."MsgSecurityMX"
        WHERE "IdMessageGet" = ?
    '''

    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, message_id)
    ibm_db.execute(stmt)
    message = ""
    if ibm_db.fetch_row(stmt):
        message = ibm_db.result(stmt, 0)

    ibm_db.close(conn)

    return JsonResponse({
        "message": message
    })

def get_smp_message_admin(request, message_id):
    return get_message_admin(
        request,
        message_id,
        db_type="smp",
        default_schema="BIKL"
    )





@csrf_exempt
def run_test(request):

    data = json.loads(request.body)
    selected_tests = data.get("tests", [])
    browsers = data.get("browsers", ["chrome", "firefox", "edge"])
    result = run_pytest(selected_tests, browsers)

    return JsonResponse(result)


@csrf_exempt
def api_run_tests(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST required"},
            status=405
        )

    body = json.loads(request.body)
    tests = body.get("tests", [])
    browsers = body.get("browsers", ["chrome", "firefox", "edge"])
    result = run_pytest(tests, browsers)

    return JsonResponse(result)
