import os
import sys
import csv
import pprint
import json
import argparse
from opyrnd.api_backed import ApiBacked
from opyrnd.workfile import WorkFile
from opyrnd.entities import Entity
from opyrnd.jobs import JobRun, JobType
from opyrnd.exceptions import OpyrndException,DoesNotExist,CouldNotConnect

"""
Deletes a All Entities and WorkFiles generated by
 an RNA_Seq JobRun that were loaded by the post_nf_output 
 script
"""

def delete_stuff(job_run_id):
    jr = JobRun.get_by_system_id(job_run_id)
    out_ids = []
    deleted_wfs = 0
    print(f"JobRun {job_run_id} GeneratedWorkFileIds:")
    print(jr.allGeneratedWorkFileIds)
    if hasattr(jr,'allGeneratedWorkFileIds'):
        for wfid in jr.allGeneratedWorkFileIds:
            try:
                wf = WorkFile.get_by_system_id(wfid)
                d = wf.delete()
                deleted_wfs = deleted_wfs + 1
                print(f"DELETED WorkFile {wfid} ")
            except DoesNotExist as de:
                print(f"Attempting to delete WorkFile {wfid} but does not exist")
            except OpyrndException as oe:
                print(oe)
    else:
        print("No WorkFiles to Delete in allGeneratedWorkFileIds")
        sys.exit()

    #all of the dangling entities
    print("Entity Deletes")
    deleted_ents = 0
    for wfid in jr.allGeneratedWorkFileIds:
        e = Entity.get_by({'result_file': str(wfid)})
        if len(e) == 1:
            eid = e[0].entity_id
            d = Entity.delete_by_id(eid)
            deleted_ents = deleted_ents + 1
            print(f"DELETED Entity {eid} {d}")
        else:
            print(f"NO Entities Referencing WorkFile {wfid}")

    # yeah - I know .. it will be only 1
    deleted_jr = JobRun.delete_by_id(job_run_id)

    print("DONE")
    print(f"{deleted_wfs} WorkFiles Deleted")
    print(f"{deleted_ents} Entities Deleted")
    print(f"{deleted_jr} JobRun Deleted")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-id",'--job_run_id', type=int,
                        help="Integer Job Run ID:",required=True)
    parser.add_argument("-c","--operend_config_file", type=str,
                        help="The configuration ini file containing Operend configuration parameters",
                        required=True)
    args = parser.parse_args()
    ApiBacked.configure_from_file(args.operend_config_file)
    delete_stuff(args.job_run_id)
