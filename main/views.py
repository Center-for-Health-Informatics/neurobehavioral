import requests
import json

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from redcap_importer.models import RedcapConnection

from . import models


def run_request(content, oConnection, addl_options={}):
    addl_options['content'] = content
    addl_options['token'] = oConnection.get_api_token()
    addl_options['format'] = 'json'
    addl_options['returnFormat'] = 'json'
    return requests.post(oConnection.api_url.url, addl_options).json()

study_map = {
    "0": "U54 P1",
    "1": "U54 K23 Ernie",
    "2": "DDNR K23 Schmitt",
    "3": "DDNR RO1 UCLA Carlos",
    "4": "P50",
    "5": "P50 Long",
    "6": "P50 Drug",
    "7": "Hessl RO1",
    "8": "MRIR",
    "9": "MRIDD",
    "10": "NIRS",
    "11": "BIO",
    "12": "DDNR",
    "13": "NIRDD",
}

@login_required
def home(request):
    context = {}
    if request.method == "POST":
        oConnection = RedcapConnection.objects.get(unique_name="main_repo")
        options = {
            'fields[0]': 'record_id',
            'fields[1]': 'studyids_studies',
            'fields[2]': 'visit_info_age',
            'fields[3]': 'visit_info_date',
            'fields[4]': 'visit_info_studies',
            # 'forms[0]': 'visit_information',
            'events[0]': 'all_measures_arm_1',
            'events[1]': 'subject_info_arm_1',
        }
        response = run_request("record", oConnection, options)
        print(json.dumps(response))
        data_table = []
        for entry in response:
            output = []
            output.append(entry["record_id"])
            output.append(entry["visit_info_age"])
            subject_studies = []
            visit_studies = []
            for i in range(13):
                field_name = "studyids_studies___" + str(i)
                if entry.get(field_name) == "1":
                    subject_studies.append(study_map[str(i)])
                field_name = "visit_info_studies___" + str(i)
                if entry.get(field_name) == "1":
                    visit_studies.append(study_map[str(i)])
            output.append(",".join(subject_studies))
            output.append(",".join(visit_studies))
            data_table.append(output)
        context["data_table"] = data_table
    return render(request, 'main/home.html', context)

@login_required
def update_new_visits(request):
    if request.method != "POST":
        return redirect("home")
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    options = {
        'forms[1]': 'visit_information',
        'fields[1]': 'record_id',
        # 'fields[3]': 'visit_info_date',
        # 'fields[4]': 'visit_info_studies',
        'events[0]': 'all_measures_arm_1',
    }
    response = run_request("record", oConnection, options)
    dataset = []
    for entry in response:
        # ignore record if no instance value
        if not entry["redcap_repeat_instance"]:
            continue
        # don't run already completed ones
        oCompletedVisit = models.CompletedVisit.objects.filter(record_id=entry["record_id"],
                instance=entry["redcap_repeat_instance"]).first()
        if oCompletedVisit:
            continue
        output = {}
        output["record_id"] = entry["record_id"]
        output["visit_age"] = entry["visit_info_age"]
        output["instance"] = entry["redcap_repeat_instance"]
        visit_studies = []
        instruments = []
        for oStudy in models.Study.objects.all():
            field_name = "visit_info_studies___" + str(oStudy.study_number)
            if entry.get(field_name) == "1":
                visit_studies.append(oStudy)
                for oStudyInstrument in oStudy.studyinstrument_set.all():
                    # TODO: also need to check age
                    oInstrument = oStudyInstrument.instrument
                    if oInstrument not in instruments:
                        instruments.append(oInstrument)
        output["visit_studies"] = visit_studies
        output["instruments"] = instruments
        dataset.append(output)
    for entry in dataset:
        for oInstrument in entry["instruments"]:
            print(f"create instrument {oInstrument} on record {entry['record_id']}, instance {entry['instance']}")
            # TODO: actually create in redcap
            oVisit = models.CompletedVisit(record_id=entry['record_id'], instance=entry['instance'])
            oVisit.save()

    messages.success(request, "update complete")
    return redirect("home")
