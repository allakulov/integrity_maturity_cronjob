from flask import Flask, request, render_template, jsonify
import os
import config
#from coconut import LimeAPI, Survey, Workbook
from lime import LimeAPI
from survey import Survey
from workbook import Workbook
import base64
import json
import traceback
from contextlib import contextmanager
from pprint import pprint
import pandas as pd

import pendulum
from loguru import logger
from tinyrpc import InvalidReplyError
from tinyrpc.client import RPCClient, RPCProxy
from tinyrpc.protocols.jsonrpc import (
    JSONRPCSuccessResponse,
    JSONRPCErrorResponse,
    JSONRPCProtocol,
)
from tinyrpc.transports.http import HttpPostClientTransport


app = Flask(__name__)

env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)


@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'GET':
        secret_key = app.config.get("LIMESURVEY_PASS")
        # Create a LimeAPI instance
        lime = LimeAPI(
                url="https://win-s.limequery.com/admin/remotecontrol",
                username="Water_Integrity",
                password=secret_key
            )

        # override survey completion status and response type
        lime = lime.export_responses(survey_id=669928, completion_status = 'complete',  response_type = "short")

        class ChildLime(LimeAPI):
            def export_responses(
                self,
                survey_id: int,
                language_code: str = None,
                completion_status: str = "complete",
                heading_type: str = "code",
                response_type: str = "short",
                from_response_id: int = None,
                to_response_id: int = None,
                fields=None,
            ):
                with self.request_ctx("get_survey_properties"):
                    _completion_statuses = ["complete", "incomplete", "all"]
                    _heading_types = ["code", "full", "abbreviated"]
                    _response_types = ["short", "long"]

                    result_b64 = self.rpc_proxy.export_responses(
                        sSessionKey=self.session_key,
                        iSurveyID=survey_id,
                        sDocumentType="json",
                        sLanguageCode=language_code,
                        sCompletionStatus=completion_status,
                        sHeadingType=heading_type,
                        sResponseType=response_type,
                        iFromResponseID=from_response_id,
                        iToResponseID=to_response_id,
                        aFields=fields,
                    )
                    result_utf8 = base64.b64decode(result_b64).decode("utf-8")
                    result_json = json.loads(result_utf8)
                    result_json = result_json["responses"]
                    rows = []
                    for id_survey_map in result_json:
                        for survey in id_survey_map.values():
                            rows.append(survey)
                    return rows

        # Create a LimeAPI instance
        lime2 = ChildLime(
                url="https://win-s.limequery.com/admin/remotecontrol",
                username="Water_Integrity",
                password="WINls_admin2020!"
            )

        # Create the survey instance
        survey = Survey(survey_id=669928, lime_api=lime2)



        # Load questions, responses, survey info
        survey.load_data()

        survey.to_csv("survey.csv")
        df = pd.read_csv('survey.csv')
        df = df.to_dict()


        return df
    return None

if __name__ == '__main__':
    app.run(debug=True)