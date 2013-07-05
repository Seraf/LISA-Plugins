import requests, json, base64

LOGIN = "XXXX"
PASSWORD = "XXXX"

pluginlist_metadata = []
error = 0
repo = requests.get('https://api.github.com/repos/Seraf/LISA-Plugins/contents/', auth=(LOGIN, PASSWORD))
if(repo.ok):
    repoItems = json.loads(repo.text or repo.content)
    for item in repoItems:
        if(item['type'] == 'dir' or \
           (item['type'] == 'file' and 'Seraf/LISA-Plugins' not in item['git_url'])):
            if(item['type'] == 'dir'):
                jsonreq = requests.get( str(item['git_url']).split('git/trees')[0]+'contents/'+item['name']+'/'+ \
                                        str(item['name']).lower()+'.json', auth=(LOGIN, PASSWORD))
            elif((item['type'] == 'file' and 'Seraf/LISA-Plugins' not in item['git_url'])):
                print str(item['git_url']).split('git/trees/')[0] + \
                      'commits/' + str(item['git_url']).split('git/trees/')[1]
                commit = requests.get(str(item['git_url']).split('git/trees/')[0] + \
                                      'commits/' + str(item['git_url']).split('git/trees/')[1], \
                                      auth=(LOGIN, PASSWORD))
                if(commit.ok):
                    commit_json = json.loads(commit.text or commit.content)
                    for file in commit_json['files']:
                        if file['filename'] == (str(item['name']).lower() + '.json'):
                            jsonreq = requests.get( file['contents_url'], auth=(LOGIN, PASSWORD))
            else:
                pass
            if(jsonreq.ok):
                json_plugin = json.loads(jsonreq.text or jsonreq.content)
                metadata = json.loads(base64.b64decode(json_plugin['content']))
                plugin = {
                            'name': metadata['name'], 'version': metadata['version'],
                            'author': metadata['author'], 'lang': metadata['lang'], 'sha': item['sha'],
                            'url': str(item['html_url']).split('/tree')[0] + '.git'
                         }
                print "Adding : " + plugin['name'] + " version " + plugin['version']
                for key in metadata:
                    if('description' in key):
                        plugin[key] = metadata[key]
                pluginlist_metadata.append(plugin)
            else:
                error =+ 1
    content_base64 = base64.b64encode(json.dumps(pluginlist_metadata))
    list_json = requests.get('https://api.github.com/repos/Seraf/LISA-Plugins/contents/plugin_list.json', \
                             auth=(LOGIN, PASSWORD))
    if(list_json.ok):
        original_list_json = json.loads(list_json.text)
        original_sha_list = original_list_json['sha']
        original_content_base64 = base64.b64encode(base64.b64decode(original_list_json['content']))
    else:
        error =+ 1
    data_json = {   'message': 'Generating new plugin list',
                    'content': content_base64,
                    'sha': original_sha_list,
                    'path': '/plugin_list.json',
    }
    if content_base64 != original_content_base64:
        print "Different content. Uploading file.\n"
        if error == 0:
            send_file = requests.put('https://api.github.com/repos/Seraf/LISA-Plugins/contents/plugin_list.json', \
                         auth=(LOGIN, PASSWORD), data=json.dumps(data_json))
    else:
        print "Same content. Do nothing.\n"
