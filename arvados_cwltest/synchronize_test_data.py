import argparse
import os

import arvados


def get_collections(projects):
    items = {}

    for instance, uuid in projects.items():
        api = arvados.api('v1', host=f'api.{instance}.roche.com', token=os.environ['ARVADOS_API_TOKEN'])
        collections = arvados.util.keyset_list_all(api.collections().list, filters=[['owner_uuid', '=', uuid]])
        for collection in collections:
            values = items.setdefault(collection['name'], {i: None for i in projects.keys()})
            values[instance] = {
                'uuid': collection['uuid'],
                'pdh': collection['portable_data_hash'],
                'modified_at': collection['modified_at'],
            }
    return items


def copy_files(projects, src_uuid, src_instance, dst_instance, dst_uuid=None):
    src_api = arvados.api('v1', host=f'api.{src_instance}.roche.com', token=os.environ['ARVADOS_API_TOKEN'])
    dst_api = arvados.api('v1', host=f'api.{dst_instance}.roche.com', token=os.environ['ARVADOS_API_TOKEN'])
    src_col = arvados.collection.CollectionReader(src_uuid, api_client=src_api)
    if dst_uuid:
        dst_col = arvados.collection.Collection(dst_uuid, api_client=dst_api)
    else:
        dst_col = arvados.collection.Collection(api_client=dst_api)
    for file in src_col.all_files():
        file_path = f"{file.stream_name()}/{file.name}"[2:]
        dst_col.copy(file_path, file_path, source_collection=src_col, overwrite=True)
    if dst_uuid:
        dst_col.save()
    else:
        c = src_api.collections().get(uuid=src_col.manifest_locator()).execute()
        dst_col.save_new(name=c['name'], owner_uuid=projects[dst_instance])


def update_projects(projects, collections, dry_run=True):
    for collection_name, instances in collections.items():
        last_modified = sorted([i for i in instances.values() if i], key=lambda x: x.get('modified_at'), reverse=True)[0]
        last_modified_instance = last_modified['uuid'].split('-')[0]
        print(f"Found newest collection {collection_name} on {last_modified_instance}")
        for instance, item in instances.items():
            if item and item['pdh'] == last_modified['pdh']:
                continue
            if item:
                print(f"\tUpdating collection {item['uuid']} on {instance}")
                if not dry_run:
                    copy_files(
                        projects,
                        src_uuid=last_modified['uuid'],
                        src_instance=last_modified_instance,
                        dst_uuid=item['uuid'],
                        dst_instance=instance
                    )
            else:
                print(f"\tNot found {collection_name} on {instance}, creating")
                if not dry_run:
                    copy_files(
                        projects,
                        src_uuid=last_modified['uuid'],
                        src_instance=last_modified_instance,
                        dst_instance=instance
                    )


def synchronize():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', help="Run a script without updating Arvados projects")
    parser.add_argument('project_uuids', nargs='*', help="List project uuids where test data is stored")
    args = parser.parse_args()
    projects = {uuid.split('-')[0]: uuid for uuid in args.project_uuids}
    collections = get_collections(projects)
    update_projects(projects, collections, dry_run=args.dry_run)

