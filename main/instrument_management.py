
import datetime

from redcap_importer.models import RedcapConnection

from . import utils
from . import models


def create_instruments_for_one_visit(record_id, redcap_repeat_instance):
    response = _create_or_ignore_instruments(record_id, redcap_repeat_instance)
    return response

def create_instruments_for_all_incomplete():
    response = _create_or_ignore_instruments()
    return response

def ignore_instruments_for_one_visit(record_id, redcap_repeat_instance):
    response = _create_or_ignore_instruments(record_id, redcap_repeat_instance, ignore=True)
    return response

def ignore_instruments_for_all_incomplete():
    response = _create_or_ignore_instruments(ignore=True)
    return response

def _create_or_ignore_instruments(record_id=None, redcap_repeat_instance=None, ignore=False):
    """
    Generates instruments for any visits that haven't been run or ignored yet. Can do one
    specific visit by specifying record_id and redcap_repeat_instance.
    """
    # get a list of visit_information records
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    options = {
        'forms[1]': 'visit_information',
        'fields[1]': 'record_id',
        # 'fields[3]': 'visit_info_date',
        # 'fields[4]': 'visit_info_studies',
        'events[0]': 'all_measures_arm_1',
    }
    response = utils.run_request("record", oConnection, options)

    # do some other stuff
    dataset = []
    errors = []
    for entry in response:
        # ignore record if no instance value or if we're limiting which visits to run
        if not entry["redcap_repeat_instance"]:
            continue
        if record_id and int(entry["record_id"]) != record_id:
            continue
        if redcap_repeat_instance and int(
            entry["redcap_repeat_instance"]) != redcap_repeat_instance:
            continue
        output = _determine_instruments_for_one_visit(entry)
        if output:
            dataset.append(output)
    for entry in dataset:
        if ignore:
            _ignore_one_visit(entry)
        else:
            new_errors = _generate_instruments_for_one_visit(entry)
            if new_errors:
                errors = errors + new_errors
    return errors


def _ignore_one_visit(entry):
    """
    Creates a CompletedVisit entry flagged with ignore=True, and doesn't create any instruments
    for it.
    """
    oVisit = models.CompletedVisit(record_id=entry['record_id'], instance=entry['instance'],
                                   visit_date=entry["visit_date"], ignore=True)
    oVisit.save()

def _generate_instruments_for_one_visit(entry):
    """
    Takes the output from determine_instruments_for_one_visit() and uses it to actually generate
    the instruments in REDCap and flag the visit as complete in our database
    """
    errors = []
    oVisit = models.CompletedVisit(record_id=entry['record_id'], instance=entry['instance'],
                                   visit_date=entry["visit_date"])
    oVisit.save()
    oConnection = RedcapConnection.objects.get(unique_name="main_repo")
    for oInstrument in entry["instruments"]:
        # print(f"create instrument {oInstrument} on record {entry['record_id']}, instance {entry['instance']}")
        instance, response = utils.create_instrument(oConnection, oInstrument, entry["record_id"],
                                                     entry["visit_date"])
        # print("resp", response)
        oCreated = models.CreatedInstrument(visit=oVisit,
                                            instrument_name=oInstrument.instrument_name,
                                            instance=instance)
        if "count" in response and response["count"] == 1:
            oCreated.save()
        else:
            record_id = entry['record_id']
            inst = entry['instance']
            instr = oInstrument.instrument_name
            errors.append(f"record_id {record_id} visit instance {inst} failed to create instrument {instr}: {response}")
    return errors

def _determine_instruments_for_one_visit(entry):
    """
    Generates a dictionary with all the info needed to create instruments, but doesn't actually
    create the instruments.
    """
    # don't run already completed ones
    oCompletedVisit = models.CompletedVisit.objects.filter(
        record_id=entry["record_id"],
        instance=entry["redcap_repeat_instance"]
    ).first()
    output = {}
    if oCompletedVisit:
        return output
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
    return output


