import requests
import json
import datetime

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import ProtectedError

from redcap_importer.models import RedcapConnection

from . import models
from . import utils
from . import forms



@login_required
def home(request):
    return redirect("manage_rules")


@login_required
def test_rules(request):
    context = {}
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    options = {
        'forms[1]': "visit_information",
        'fields[1]': 'record_id',
        'events[0]': 'all_measures_arm_1',
    }
    response = utils.run_request("record", oConnection, options)
    visits = []
    for entry in response:
        if not entry["redcap_repeat_instance"]:
            continue
        visit_studies = []
        for i in range(13):
            field_name = "visit_info_studies___" + str(i)
            if entry.get(field_name) == "1":
                oStudy = models.Study.objects.filter(study_number=i).first()
                if oStudy:
                    visit_studies.append(str(oStudy))
                else:
                    visit_studies.append(str(i))
        entry["visit_info_studies"] = visit_studies
        entry["group_name"] = entry["visit_info_group_mem"]
        if entry["visit_info_group_mem"]:
            oGroup = models.Group.objects.filter(group_number=entry["visit_info_group_mem"]).first()
            if oGroup:
                entry["group_name"] = str(oGroup)
        oVisit = models.CompletedVisit.objects.filter(record_id=entry["record_id"], instance=int(entry["redcap_repeat_instance"])).first()
        entry["completed_visit"] = oVisit
        visits.append(entry)
    context["visits"] = visits
    context["current_page"] = "test_rules"
    return render(request, 'main/test_rules.html', context)

@login_required
def manage_rules(request):
    qRule = models.InstrumentCreationRule.objects.all()
    context = {
        "current_page": "manage_rules",
        "qObj": qRule,
    }
    return render(request, 'main/manage_rules.html', context)

@login_required
def create_rule(request):
    if request.method == "POST":
        form = forms.InstrumentCreationRuleForm(request.POST)
        if form.is_valid():
            oObj = form.save()
            messages.success(request, "Rule '{}' was successfully created.".format(oObj))
            return redirect("manage_rules")
    else:
        form = forms.InstrumentCreationRuleForm()
    context = {
        "form": form,
        "current_page": "rules",
    }
    return render(request, 'main/create_rule.html', context)

@login_required
def edit_rule(request, rule_id):
    oRule = get_object_or_404(models.InstrumentCreationRule, pk=rule_id)
    if request.method == "POST":
        form = forms.InstrumentCreationRuleForm(request.POST, instance=oRule)
        if form.is_valid():
            oRule = form.save()
            messages.success(request, "Rule '{}' was successfully edited.".format(oRule))
            return redirect("manage_rules")
    else:
        form = forms.InstrumentCreationRuleForm(instance=oRule)
    context = {
        "form": form,
        "current_page": "rules",
    }
    return render(request, "main/edit_rule.html", context)

@login_required
def delete_rule(request, rule_id):
    oRule = get_object_or_404(models.InstrumentCreationRule, pk=rule_id)
    if request.method == "POST":
        try:
            rule_name = str(oRule)
            oRule.delete()
            messages.success(request, "Notification '{}' has been deleted.".format(rule_name))
        except ProtectedError:
            message = ("Cannot delete this rule because there are other tables "
                       "referencing it.")
            messages.error(request, message)
    return redirect("manage_rules")

@login_required
def update_list_of_instruments(request):
    if request.method != "POST":
        return redirect("manage_rules")
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")

    # update study list
    options = {
        'arms[0]': '1',
    }
    response = utils.run_request("formEventMapping", oConnection, options)
    for entry in response:
        if entry["unique_event_name"] == "all_measures_arm_1" and entry["form"] != "visit_information":
            field_name = get_random_field(entry["form"])
            if field_name is None:
                messages.error(request, f"no visit date field found for instrument {entry['form']}")
                continue
            # print("fn", entry["form"], field_name)
            oInstrument = models.Instrument.objects.filter(instrument_name=entry["form"]).first()
            if not oInstrument:
                oInstrument = models.Instrument(instrument_name=entry["form"])
            oInstrument.instrument_field = field_name
            oInstrument.save()
    messages.success(request, "update complete")
    return redirect("manage_rules")

def get_random_field(instrument_name):
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    options = {
        'forms[0]': instrument_name,
    }
    response = utils.run_request("metadata", oConnection, options)
    for entry in response:
        if "visit_date" in entry["field_name"]:
            field_name = entry["field_name"]
            return field_name
    return None
    # raise ValueError(f"couldn't find a field for instrument {instrument_name}")



@login_required
def update_visit_info_metadata(request):
    """ Update options for visit_info_studies and visit_info_group_mem """
    if request.method != "POST":
        return redirect("manage_rules")
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")

    # update study list
    options = {
        'fields[0]': 'visit_info_studies',
    }
    response = utils.run_request("metadata", oConnection, options)
    if len(response) != 1 or not "select_choices_or_calculations" in response[0]:
        messages.error(request, "Unable to get the list of studies from REDCap")
    study_str = response[0]["select_choices_or_calculations"]
    studies = study_str.split(" | ")
    # set all to missing and then verify which are present
    for oStudy in models.Study.objects.all():
        oStudy.missing = True
        oStudy.save()
    for study in studies:
        study_number, study_name = study.split(", ", 1)
        oStudy, created = models.Study.objects.get_or_create(
            study_number=int(study_number),
            study_name=study_name
        )
        oStudy.missing = False
        oStudy.save()

    # update group list
    options = {
        'fields[0]': 'visit_info_group_mem',
    }
    response = utils.run_request("metadata", oConnection, options)
    if len(response) != 1 or not "select_choices_or_calculations" in response[0]:
        messages.error(request, "Unable to get the list of studies from REDCap")
    group_str = response[0]["select_choices_or_calculations"]
    groups = group_str.split(" | ")
    # set all to missing and then verify which are present
    for oGroup in models.Group.objects.all():
        oGroup.missing = True
        oGroup.save()
    for group in groups:
        group_number, group_name = group.split(", ", 1)
        oGroup, created = models.Group.objects.get_or_create(
            group_number=int(group_number),
            group_name=group_name
        )
        oGroup.missing = False
        oGroup.save()
    messages.success(request, "update complete")
    return redirect("manage_rules")

@login_required
def create_instruments(request, record_id=None, redcap_repeat_instance=None):
    """
    Looks for new visits and creates appropriate instruments in REDCap
    """
    if request.method != "POST":
        return redirect("test_rules")
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    options = {
        'forms[1]': 'visit_information',
        'fields[1]': 'record_id',
        # 'fields[3]': 'visit_info_date',
        # 'fields[4]': 'visit_info_studies',
        'events[0]': 'all_measures_arm_1',
    }
    response = utils.run_request("record", oConnection, options)
    dataset = []
    for entry in response:
        # ignore record if no instance value or if we're limiting which visits to run
        if not entry["redcap_repeat_instance"]:
            continue
        if record_id and int(entry["record_id"]) != record_id:
            continue
        if redcap_repeat_instance and int(entry["redcap_repeat_instance"]) != redcap_repeat_instance:
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
        output["visit_group"] = entry["visit_info_group_mem"]
        output["visit_date"] = entry.get("visit_info_date")
        if not output["visit_date"]:
            output["visit_date"] = datetime.date(1970, 1, 1)
        visit_studies = []
        instruments = []
        for oStudy in models.Study.objects.all():
            field_name = "visit_info_studies___" + str(oStudy.study_number)
            if entry.get(field_name) == "1":
                visit_studies.append(oStudy)
                for oRule in oStudy.instrumentcreationrule_set.all():
                    if output["visit_age"]:
                        if oRule.min_age and float(output["visit_age"]) <= oRule.min_age:
                            continue
                        if oRule.max_age and float(output["visit_age"]) >= oRule.max_age:
                            continue
                    if output["visit_group"] and oRule.group:
                        if int(output["visit_group"]) != oRule.group.group_number:
                            continue
                    qInstrument = oRule.instruments.all()
                    for oInstrument in qInstrument:
                        if oInstrument not in instruments:
                            instruments.append(oInstrument)
        output["visit_studies"] = visit_studies
        output["instruments"] = instruments
        dataset.append(output)
    for entry in dataset:
        oVisit = models.CompletedVisit(record_id=entry['record_id'], instance=entry['instance'], visit_date=entry["visit_date"])
        oVisit.save()
        for oInstrument in entry["instruments"]:
            # print(f"create instrument {oInstrument} on record {entry['record_id']}, instance {entry['instance']}")
            instance, response = utils.create_instrument(oConnection, oInstrument, entry["record_id"], entry["visit_date"])
            # print("resp", response)
            oCreated = models.CreatedInstrument(visit=oVisit, instrument_name=oInstrument.instrument_name, instance=instance)
            if "count" in response and response["count"] == 1:
                oCreated.save()
            else:
                record_id = entry['record_id']
                inst = entry['instance']
                instr = oInstrument.instrument_name
                messages.error(request, f"record_id {record_id} visit instance {inst} failed to create instrument {instr}: {response}")
    messages.success(request, "update complete")
    return redirect("test_rules")

@login_required
def delete_instruments(request, record_id=None, redcap_repeat_instance=None):
    """
    Goes through logs of created instruments and attempts to un-create them. Useful for starting
    over while testing behavior.
    """
    if request.method != "POST":
        return redirect("test_rules")
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    visits_to_delete = []
    created_to_delete = []
    # delete from redcap
    qVisit = models.CompletedVisit.objects.all()
    if record_id:
        qVisit = qVisit.filter(record_id=record_id)
    if redcap_repeat_instance:
        qVisit = qVisit.filter(instance=redcap_repeat_instance)
    for oVisit in qVisit:
        visit_delete_successful = True
        for oCreated in oVisit.createdinstrument_set.exclude(successful=False):
            successful = utils.delete_instrument(oConnection, oVisit.record_id, oCreated.instrument_name, oCreated.instance)
            if successful:
                created_to_delete.append(oCreated)
            else:
                visit_delete_successful = False
        if visit_delete_successful:
            visits_to_delete.append(oVisit)
    # delete from logs
    for oCreated in created_to_delete:
        oCreated.delete()
    for oVisit in visits_to_delete:
        oVisit.delete()
    messages.success(request, "rollback complete")
    return redirect("test_rules")









