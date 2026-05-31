2026-05-04T03:55:56.8713664Z Current runner version: '2.334.0'
2026-05-04T03:55:56.8747623Z ##[group]Runner Image Provisioner
2026-05-04T03:55:56.8748740Z Hosted Compute Agent
2026-05-04T03:55:56.8749674Z Version: 20260213.493
2026-05-04T03:55:56.8750645Z Commit: 5c115507f6dd24b8de37d8bbe0bb4509d0cc0fa3
2026-05-04T03:55:56.8751654Z Build Date: 2026-02-13T00:28:41Z
2026-05-04T03:55:56.8752811Z Worker ID: {3ce33d34-8bad-45cf-80fe-35b54689c69a}
2026-05-04T03:55:56.8754142Z Azure Region: eastus
2026-05-04T03:55:56.8754978Z ##[endgroup]
2026-05-04T03:55:56.8756792Z ##[group]Operating System
2026-05-04T03:55:56.8757864Z Ubuntu
2026-05-04T03:55:56.8758549Z 24.04.4
2026-05-04T03:55:56.8759223Z LTS
2026-05-04T03:55:56.8760089Z ##[endgroup]
2026-05-04T03:55:56.8760789Z ##[group]Runner Image
2026-05-04T03:55:56.8761645Z Image: ubuntu-24.04
2026-05-04T03:55:56.8762492Z Version: 20260413.86.1
2026-05-04T03:55:56.8764525Z Included Software: https://github.com/actions/runner-images/blob/ubuntu24/20260413.86/images/ubuntu/Ubuntu2404-Readme.md
2026-05-04T03:55:56.8766803Z Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu24%2F20260413.86
2026-05-04T03:55:56.8768181Z ##[endgroup]
2026-05-04T03:55:56.8769948Z ##[group]GITHUB_TOKEN Permissions
2026-05-04T03:55:56.8773400Z Contents: read
2026-05-04T03:55:56.8774400Z Metadata: read
2026-05-04T03:55:56.8775216Z Packages: read
2026-05-04T03:55:56.8776038Z ##[endgroup]
2026-05-04T03:55:56.8778593Z Secret source: Actions
2026-05-04T03:55:56.8779955Z Prepare workflow directory
2026-05-04T03:55:56.9233898Z Prepare all required actions
2026-05-04T03:55:56.9288967Z Getting action download info
2026-05-04T03:55:57.2197898Z Download action repository 'actions/checkout@v4' (SHA:34e114876b0b11c390a56381ad16ebd13914f8d5)
2026-05-04T03:55:57.3448451Z Download action repository 'actions/setup-python@v5' (SHA:a26af69be951a213d495a4c3e4e4022e16d87065)
2026-05-04T03:55:57.5304709Z Complete job name: Unit and Integration Tests
2026-05-04T03:55:57.6008262Z ##[group]Run actions/checkout@v4
2026-05-04T03:55:57.6009149Z with:
2026-05-04T03:55:57.6009646Z   repository: maltidodia-design/Dockerized-Mock-project
2026-05-04T03:55:57.6010431Z   token: ***
2026-05-04T03:55:57.6010816Z   ssh-strict: true
2026-05-04T03:55:57.6011206Z   ssh-user: git
2026-05-04T03:55:57.6011593Z   persist-credentials: true
2026-05-04T03:55:57.6012032Z   clean: true
2026-05-04T03:55:57.6012418Z   sparse-checkout-cone-mode: true
2026-05-04T03:55:57.6012886Z   fetch-depth: 1
2026-05-04T03:55:57.6013472Z   fetch-tags: false
2026-05-04T03:55:57.6013869Z   show-progress: true
2026-05-04T03:55:57.6014255Z   lfs: false
2026-05-04T03:55:57.6014609Z   submodules: false
2026-05-04T03:55:57.6015008Z   set-safe-directory: true
2026-05-04T03:55:57.6015805Z ##[endgroup]
2026-05-04T03:55:57.7135420Z Syncing repository: maltidodia-design/Dockerized-Mock-project
2026-05-04T03:55:57.7137228Z ##[group]Getting Git version info
2026-05-04T03:55:57.7138182Z Working directory is '/home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project'
2026-05-04T03:55:57.7139298Z [command]/usr/bin/git version
2026-05-04T03:55:57.7179786Z git version 2.53.0
2026-05-04T03:55:57.7203925Z ##[endgroup]
2026-05-04T03:55:57.7218466Z Temporarily overriding HOME='/home/runner/work/_temp/f9ac127e-130e-48e3-a35e-8070d81e1c21' before making global git config changes
2026-05-04T03:55:57.7220501Z Adding repository directory to the temporary git global config as a safe directory
2026-05-04T03:55:57.7224025Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project
2026-05-04T03:55:57.7257693Z Deleting the contents of '/home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project'
2026-05-04T03:55:57.7260558Z ##[group]Initializing the repository
2026-05-04T03:55:57.7265128Z [command]/usr/bin/git init /home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project
2026-05-04T03:55:57.7324972Z hint: Using 'master' as the name for the initial branch. This default branch name
2026-05-04T03:55:57.7326460Z hint: will change to "main" in Git 3.0. To configure the initial branch name
2026-05-04T03:55:57.7327715Z hint: to use in all of your new repositories, which will suppress this warning,
2026-05-04T03:55:57.7328403Z hint: call:
2026-05-04T03:55:57.7328762Z hint:
2026-05-04T03:55:57.7329601Z hint: 	git config --global init.defaultBranch <name>
2026-05-04T03:55:57.7330459Z hint:
2026-05-04T03:55:57.7331260Z hint: Names commonly chosen instead of 'master' are 'main', 'trunk' and
2026-05-04T03:55:57.7332585Z hint: 'development'. The just-created branch can be renamed via this command:
2026-05-04T03:55:57.7333810Z hint:
2026-05-04T03:55:57.7334349Z hint: 	git branch -m <name>
2026-05-04T03:55:57.7334906Z hint:
2026-05-04T03:55:57.7335466Z hint: Disable this message with "git config set advice.defaultBranchName false"
2026-05-04T03:55:57.7336589Z Initialized empty Git repository in /home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project/.git/
2026-05-04T03:55:57.7339395Z [command]/usr/bin/git remote add origin https://github.com/maltidodia-design/Dockerized-Mock-project
2026-05-04T03:55:57.7368515Z ##[endgroup]
2026-05-04T03:55:57.7369534Z ##[group]Disabling automatic garbage collection
2026-05-04T03:55:57.7372340Z [command]/usr/bin/git config --local gc.auto 0
2026-05-04T03:55:57.7401490Z ##[endgroup]
2026-05-04T03:55:57.7402236Z ##[group]Setting up auth
2026-05-04T03:55:57.7408086Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-05-04T03:55:57.7438381Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-05-04T03:55:57.7735765Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-05-04T03:55:57.7766528Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-05-04T03:55:57.7999102Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-05-04T03:55:57.8030916Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-05-04T03:55:57.8273693Z [command]/usr/bin/git config --local http.https://github.com/.extraheader AUTHORIZATION: basic ***
2026-05-04T03:55:57.8309739Z ##[endgroup]
2026-05-04T03:55:57.8310488Z ##[group]Fetching the repository
2026-05-04T03:55:57.8318509Z [command]/usr/bin/git -c protocol.version=2 fetch --no-tags --prune --no-recurse-submodules --depth=1 origin +9f73350349fb197630bbe180245308a30ba13de8:refs/remotes/pull/2/merge
2026-05-04T03:55:58.2939624Z From https://github.com/maltidodia-design/Dockerized-Mock-project
2026-05-04T03:55:58.2941446Z  * [new ref]         9f73350349fb197630bbe180245308a30ba13de8 -> pull/2/merge
2026-05-04T03:55:58.2969963Z ##[endgroup]
2026-05-04T03:55:58.2971020Z ##[group]Determining the checkout info
2026-05-04T03:55:58.2972864Z ##[endgroup]
2026-05-04T03:55:58.2978595Z [command]/usr/bin/git sparse-checkout disable
2026-05-04T03:55:58.3018126Z [command]/usr/bin/git config --local --unset-all extensions.worktreeConfig
2026-05-04T03:55:58.3048623Z ##[group]Checking out the ref
2026-05-04T03:55:58.3050826Z [command]/usr/bin/git checkout --progress --force refs/remotes/pull/2/merge
2026-05-04T03:55:58.4846716Z Note: switching to 'refs/remotes/pull/2/merge'.
2026-05-04T03:55:58.4847459Z 
2026-05-04T03:55:58.4847991Z You are in 'detached HEAD' state. You can look around, make experimental
2026-05-04T03:55:58.4849095Z changes and commit them, and you can discard any commits you make in this
2026-05-04T03:55:58.4850249Z state without impacting any branches by switching back to a branch.
2026-05-04T03:55:58.4850908Z 
2026-05-04T03:55:58.4851464Z If you want to create a new branch to retain commits you create, you may
2026-05-04T03:55:58.4852592Z do so (now or later) by using -c with the switch command. Example:
2026-05-04T03:55:58.4853854Z 
2026-05-04T03:55:58.4854168Z   git switch -c <new-branch-name>
2026-05-04T03:55:58.4854667Z 
2026-05-04T03:55:58.4854957Z Or undo this operation with:
2026-05-04T03:55:58.4855401Z 
2026-05-04T03:55:58.4855679Z   git switch -
2026-05-04T03:55:58.4856046Z 
2026-05-04T03:55:58.4856661Z Turn off this advice by setting config variable advice.detachedHead to false
2026-05-04T03:55:58.4857904Z 
2026-05-04T03:55:58.4859199Z HEAD is now at 9f73350 Merge d3f7c4d2133a50ffb5d8e07c700e4a59d98573c7 into 92337513e466ab05ea6b72fd32024db55e29ab9f
2026-05-04T03:55:58.4862506Z ##[endgroup]
2026-05-04T03:55:58.4899061Z [command]/usr/bin/git log -1 --format=%H
2026-05-04T03:55:58.4923382Z 9f73350349fb197630bbe180245308a30ba13de8
2026-05-04T03:55:58.5240634Z ##[group]Run actions/setup-python@v5
2026-05-04T03:55:58.5241731Z with:
2026-05-04T03:55:58.5242527Z   python-version: 3.10
2026-05-04T03:55:58.5243576Z   check-latest: false
2026-05-04T03:55:58.5244743Z   token: ***
2026-05-04T03:55:58.5245592Z   update-environment: true
2026-05-04T03:55:58.5246570Z   allow-prereleases: false
2026-05-04T03:55:58.5247553Z   freethreaded: false
2026-05-04T03:55:58.5248417Z ##[endgroup]
2026-05-04T03:55:58.7006785Z ##[group]Installed versions
2026-05-04T03:55:58.7092913Z Successfully set up CPython (3.10.20)
2026-05-04T03:55:58.7093906Z ##[endgroup]
2026-05-04T03:55:58.7215664Z ##[group]Run python -m pip install --upgrade pip
2026-05-04T03:55:58.7216228Z [36;1mpython -m pip install --upgrade pip[0m
2026-05-04T03:55:58.7216621Z [36;1mpip install -r requirements.txt[0m
2026-05-04T03:55:58.7335543Z shell: /usr/bin/bash -e {0}
2026-05-04T03:55:58.7335895Z env:
2026-05-04T03:55:58.7336234Z   pythonLocation: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:55:58.7336752Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib/pkgconfig
2026-05-04T03:55:58.7337264Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:55:58.7337723Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:55:58.7338198Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:55:58.7338644Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib
2026-05-04T03:55:58.7339014Z ##[endgroup]
2026-05-04T03:56:01.4407498Z Requirement already satisfied: pip in /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages (26.0.1)
2026-05-04T03:56:01.5441880Z Collecting pip
2026-05-04T03:56:01.6052368Z   Downloading pip-26.1-py3-none-any.whl.metadata (4.6 kB)
2026-05-04T03:56:01.6122171Z Downloading pip-26.1-py3-none-any.whl (1.8 MB)
2026-05-04T03:56:01.6517061Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.8/1.8 MB 142.1 MB/s  0:00:00
2026-05-04T03:56:01.6905716Z Installing collected packages: pip
2026-05-04T03:56:01.6906565Z   Attempting uninstall: pip
2026-05-04T03:56:01.6912656Z     Found existing installation: pip 26.0.1
2026-05-04T03:56:01.7552669Z     Uninstalling pip-26.0.1:
2026-05-04T03:56:01.7620184Z       Successfully uninstalled pip-26.0.1
2026-05-04T03:56:02.6397102Z Successfully installed pip-26.1
2026-05-04T03:56:03.6463577Z Collecting Flask>=2.2 (from -r requirements.txt (line 1))
2026-05-04T03:56:03.6921742Z   Downloading flask-3.1.3-py3-none-any.whl.metadata (3.2 kB)
2026-05-04T03:56:03.7066047Z Collecting Flask_SQLAlchemy>=3.0 (from -r requirements.txt (line 2))
2026-05-04T03:56:03.7103986Z   Downloading flask_sqlalchemy-3.1.1-py3-none-any.whl.metadata (3.4 kB)
2026-05-04T03:56:03.7284414Z Collecting gunicorn>=20.1 (from -r requirements.txt (line 3))
2026-05-04T03:56:03.7321731Z   Downloading gunicorn-25.3.0-py3-none-any.whl.metadata (5.5 kB)
2026-05-04T03:56:03.7777526Z Collecting pytest>=7.0 (from -r requirements.txt (line 4))
2026-05-04T03:56:03.7814214Z   Downloading pytest-9.0.3-py3-none-any.whl.metadata (7.6 kB)
2026-05-04T03:56:03.8038945Z Collecting requests>=2.28 (from -r requirements.txt (line 5))
2026-05-04T03:56:03.8074340Z   Downloading requests-2.33.1-py3-none-any.whl.metadata (4.8 kB)
2026-05-04T03:56:03.8232896Z Collecting beautifulsoup4>=4.12.2 (from -r requirements.txt (line 6))
2026-05-04T03:56:03.8269900Z   Downloading beautifulsoup4-4.14.3-py3-none-any.whl.metadata (3.8 kB)
2026-05-04T03:56:03.8389704Z Collecting blinker>=1.9.0 (from Flask>=2.2->-r requirements.txt (line 1))
2026-05-04T03:56:03.8426097Z   Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
2026-05-04T03:56:03.8583793Z Collecting click>=8.1.3 (from Flask>=2.2->-r requirements.txt (line 1))
2026-05-04T03:56:03.8619116Z   Downloading click-8.3.3-py3-none-any.whl.metadata (2.6 kB)
2026-05-04T03:56:03.8723872Z Collecting itsdangerous>=2.2.0 (from Flask>=2.2->-r requirements.txt (line 1))
2026-05-04T03:56:03.8757897Z   Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
2026-05-04T03:56:03.8893136Z Collecting jinja2>=3.1.2 (from Flask>=2.2->-r requirements.txt (line 1))
2026-05-04T03:56:03.8930511Z   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
2026-05-04T03:56:03.9452015Z Collecting markupsafe>=2.1.1 (from Flask>=2.2->-r requirements.txt (line 1))
2026-05-04T03:56:03.9493530Z   Downloading markupsafe-3.0.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
2026-05-04T03:56:03.9678746Z Collecting werkzeug>=3.1.0 (from Flask>=2.2->-r requirements.txt (line 1))
2026-05-04T03:56:03.9724156Z   Downloading werkzeug-3.1.8-py3-none-any.whl.metadata (4.0 kB)
2026-05-04T03:56:04.2512249Z Collecting sqlalchemy>=2.0.16 (from Flask_SQLAlchemy>=3.0->-r requirements.txt (line 2))
2026-05-04T03:56:04.2555289Z   Downloading sqlalchemy-2.0.49-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (9.5 kB)
2026-05-04T03:56:04.2812559Z Collecting packaging (from gunicorn>=20.1->-r requirements.txt (line 3))
2026-05-04T03:56:04.2849704Z   Downloading packaging-26.2-py3-none-any.whl.metadata (3.5 kB)
2026-05-04T03:56:04.2981025Z Collecting exceptiongroup>=1 (from pytest>=7.0->-r requirements.txt (line 4))
2026-05-04T03:56:04.3023895Z   Downloading exceptiongroup-1.3.1-py3-none-any.whl.metadata (6.7 kB)
2026-05-04T03:56:04.3142749Z Collecting iniconfig>=1.0.1 (from pytest>=7.0->-r requirements.txt (line 4))
2026-05-04T03:56:04.3206064Z   Downloading iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
2026-05-04T03:56:04.3344405Z Collecting pluggy<2,>=1.5 (from pytest>=7.0->-r requirements.txt (line 4))
2026-05-04T03:56:04.3384869Z   Downloading pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
2026-05-04T03:56:04.3600996Z Collecting pygments>=2.7.2 (from pytest>=7.0->-r requirements.txt (line 4))
2026-05-04T03:56:04.3640068Z   Downloading pygments-2.20.0-py3-none-any.whl.metadata (2.5 kB)
2026-05-04T03:56:04.3877311Z Collecting tomli>=1 (from pytest>=7.0->-r requirements.txt (line 4))
2026-05-04T03:56:04.3912497Z   Downloading tomli-2.4.1-py3-none-any.whl.metadata (10 kB)
2026-05-04T03:56:04.5027331Z Collecting charset_normalizer<4,>=2 (from requests>=2.28->-r requirements.txt (line 5))
2026-05-04T03:56:04.5091562Z   Downloading charset_normalizer-3.4.7-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (40 kB)
2026-05-04T03:56:04.5245552Z Collecting idna<4,>=2.5 (from requests>=2.28->-r requirements.txt (line 5))
2026-05-04T03:56:04.5286765Z   Downloading idna-3.13-py3-none-any.whl.metadata (8.0 kB)
2026-05-04T03:56:04.5502484Z Collecting urllib3<3,>=1.26 (from requests>=2.28->-r requirements.txt (line 5))
2026-05-04T03:56:04.5544160Z   Downloading urllib3-2.6.3-py3-none-any.whl.metadata (6.9 kB)
2026-05-04T03:56:04.5743938Z Collecting certifi>=2023.5.7 (from requests>=2.28->-r requirements.txt (line 5))
2026-05-04T03:56:04.5781029Z   Downloading certifi-2026.4.22-py3-none-any.whl.metadata (2.5 kB)
2026-05-04T03:56:04.5955268Z Collecting soupsieve>=1.6.1 (from beautifulsoup4>=4.12.2->-r requirements.txt (line 6))
2026-05-04T03:56:04.5991008Z   Downloading soupsieve-2.8.3-py3-none-any.whl.metadata (4.6 kB)
2026-05-04T03:56:04.6153718Z Collecting typing-extensions>=4.0.0 (from beautifulsoup4>=4.12.2->-r requirements.txt (line 6))
2026-05-04T03:56:04.6189463Z   Downloading typing_extensions-4.15.0-py3-none-any.whl.metadata (3.3 kB)
2026-05-04T03:56:04.7603423Z Collecting greenlet>=1 (from sqlalchemy>=2.0.16->Flask_SQLAlchemy>=3.0->-r requirements.txt (line 2))
2026-05-04T03:56:04.7646029Z   Downloading greenlet-3.5.0-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl.metadata (3.7 kB)
2026-05-04T03:56:04.7741522Z Downloading flask-3.1.3-py3-none-any.whl (103 kB)
2026-05-04T03:56:04.7849509Z Downloading flask_sqlalchemy-3.1.1-py3-none-any.whl (25 kB)
2026-05-04T03:56:04.7903835Z Downloading gunicorn-25.3.0-py3-none-any.whl (208 kB)
2026-05-04T03:56:04.7978987Z Downloading pytest-9.0.3-py3-none-any.whl (375 kB)
2026-05-04T03:56:04.8053721Z Downloading pluggy-1.6.0-py3-none-any.whl (20 kB)
2026-05-04T03:56:04.8120881Z Downloading requests-2.33.1-py3-none-any.whl (64 kB)
2026-05-04T03:56:04.8177182Z Downloading charset_normalizer-3.4.7-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (216 kB)
2026-05-04T03:56:04.8233207Z Downloading idna-3.13-py3-none-any.whl (68 kB)
2026-05-04T03:56:04.8287612Z Downloading urllib3-2.6.3-py3-none-any.whl (131 kB)
2026-05-04T03:56:04.8342511Z Downloading beautifulsoup4-4.14.3-py3-none-any.whl (107 kB)
2026-05-04T03:56:04.8398442Z Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
2026-05-04T03:56:04.8452532Z Downloading certifi-2026.4.22-py3-none-any.whl (135 kB)
2026-05-04T03:56:04.8509585Z Downloading click-8.3.3-py3-none-any.whl (110 kB)
2026-05-04T03:56:04.8580638Z Downloading exceptiongroup-1.3.1-py3-none-any.whl (16 kB)
2026-05-04T03:56:04.8638126Z Downloading iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
2026-05-04T03:56:04.8693222Z Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
2026-05-04T03:56:04.8745945Z Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
2026-05-04T03:56:04.8803859Z Downloading markupsafe-3.0.3-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (20 kB)
2026-05-04T03:56:04.8856502Z Downloading packaging-26.2-py3-none-any.whl (100 kB)
2026-05-04T03:56:04.8912455Z Downloading pygments-2.20.0-py3-none-any.whl (1.2 MB)
2026-05-04T03:56:04.9008579Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 155.4 MB/s  0:00:00
2026-05-04T03:56:04.9045086Z Downloading soupsieve-2.8.3-py3-none-any.whl (37 kB)
2026-05-04T03:56:04.9104153Z Downloading sqlalchemy-2.0.49-cp310-cp310-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (3.2 MB)
2026-05-04T03:56:04.9296295Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.2/3.2 MB 191.6 MB/s  0:00:00
2026-05-04T03:56:04.9355010Z Downloading greenlet-3.5.0-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (613 kB)
2026-05-04T03:56:04.9407964Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 613.4/613.4 kB 116.5 MB/s  0:00:00
2026-05-04T03:56:04.9448894Z Downloading tomli-2.4.1-py3-none-any.whl (14 kB)
2026-05-04T03:56:04.9514845Z Downloading typing_extensions-4.15.0-py3-none-any.whl (44 kB)
2026-05-04T03:56:04.9571921Z Downloading werkzeug-3.1.8-py3-none-any.whl (226 kB)
2026-05-04T03:56:05.0926740Z Installing collected packages: urllib3, typing-extensions, tomli, soupsieve, pygments, pluggy, packaging, markupsafe, itsdangerous, iniconfig, idna, greenlet, click, charset_normalizer, certifi, blinker, werkzeug, sqlalchemy, requests, jinja2, gunicorn, exceptiongroup, beautifulsoup4, pytest, Flask, Flask_SQLAlchemy
2026-05-04T03:56:08.0218376Z 
2026-05-04T03:56:08.0255012Z Successfully installed Flask-3.1.3 Flask_SQLAlchemy-3.1.1 beautifulsoup4-4.14.3 blinker-1.9.0 certifi-2026.4.22 charset_normalizer-3.4.7 click-8.3.3 exceptiongroup-1.3.1 greenlet-3.5.0 gunicorn-25.3.0 idna-3.13 iniconfig-2.3.0 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 packaging-26.2 pluggy-1.6.0 pygments-2.20.0 pytest-9.0.3 requests-2.33.1 soupsieve-2.8.3 sqlalchemy-2.0.49 tomli-2.4.1 typing-extensions-4.15.0 urllib3-2.6.3 werkzeug-3.1.8
2026-05-04T03:56:08.1250551Z ##[group]Run pytest tests/
2026-05-04T03:56:08.1250827Z [36;1mpytest tests/[0m
2026-05-04T03:56:08.1275212Z shell: /usr/bin/bash -e {0}
2026-05-04T03:56:08.1275598Z env:
2026-05-04T03:56:08.1275861Z   pythonLocation: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:56:08.1276267Z   PKG_CONFIG_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib/pkgconfig
2026-05-04T03:56:08.1276658Z   Python_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:56:08.1277017Z   Python2_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:56:08.1277376Z   Python3_ROOT_DIR: /opt/hostedtoolcache/Python/3.10.20/x64
2026-05-04T03:56:08.1277727Z   LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.10.20/x64/lib
2026-05-04T03:56:08.1278017Z ##[endgroup]
2026-05-04T03:56:10.0982906Z ============================= test session starts ==============================
2026-05-04T03:56:10.0984130Z platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0
2026-05-04T03:56:10.0984683Z rootdir: /home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project
2026-05-04T03:56:10.0985066Z collected 23 items
2026-05-04T03:56:10.0985197Z 
2026-05-04T03:56:10.1525258Z tests/test_accessibility.py ...                                          [ 13%]
2026-05-04T03:56:10.1970173Z tests/test_app.py ....                                                   [ 30%]
2026-05-04T03:56:10.2675087Z tests/test_edge_cases.py ........                                        [ 65%]
2026-05-04T03:56:10.2852255Z tests/test_integration.py .                                              [ 69%]
2026-05-04T03:56:10.3183319Z tests/test_models.py ...                                                 [ 82%]
2026-05-04T03:56:10.4376643Z tests/test_routes.py ....                                                [100%]
2026-05-04T03:56:10.4377041Z 
2026-05-04T03:56:10.4377223Z =============================== warnings summary ===============================
2026-05-04T03:56:10.4377682Z tests/test_accessibility.py: 2 warnings
2026-05-04T03:56:10.4378077Z tests/test_app.py: 1 warning
2026-05-04T03:56:10.4378402Z tests/test_edge_cases.py: 4 warnings
2026-05-04T03:56:10.4378812Z tests/test_integration.py: 2 warnings
2026-05-04T03:56:10.4379176Z tests/test_models.py: 1 warning
2026-05-04T03:56:10.4379489Z tests/test_routes.py: 2 warnings
2026-05-04T03:56:10.4381388Z   /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/flask_sqlalchemy/query.py:30: LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of SQLAlchemy and becomes a legacy construct in 2.0. The method is now available as Session.get() (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
2026-05-04T03:56:10.4383812Z     rv = self.get(ident)
2026-05-04T03:56:10.4384031Z 
2026-05-04T03:56:10.4384342Z -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
2026-05-04T03:56:10.4385018Z ======================= 23 passed, 12 warnings in 1.01s ========================
2026-05-04T03:56:10.5290168Z Post job cleanup.
2026-05-04T03:56:10.7239675Z Post job cleanup.
2026-05-04T03:56:10.8242197Z [command]/usr/bin/git version
2026-05-04T03:56:10.8284025Z git version 2.53.0
2026-05-04T03:56:10.8339176Z Temporarily overriding HOME='/home/runner/work/_temp/eef89ab6-ea45-494b-9a23-d11e580fa7a0' before making global git config changes
2026-05-04T03:56:10.8340427Z Adding repository directory to the temporary git global config as a safe directory
2026-05-04T03:56:10.8345544Z [command]/usr/bin/git config --global --add safe.directory /home/runner/work/Dockerized-Mock-project/Dockerized-Mock-project
2026-05-04T03:56:10.8387370Z [command]/usr/bin/git config --local --name-only --get-regexp core\.sshCommand
2026-05-04T03:56:10.8425137Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'core\.sshCommand' && git config --local --unset-all 'core.sshCommand' || :"
2026-05-04T03:56:10.8696470Z [command]/usr/bin/git config --local --name-only --get-regexp http\.https\:\/\/github\.com\/\.extraheader
2026-05-04T03:56:10.8722536Z http.https://github.com/.extraheader
2026-05-04T03:56:10.8738032Z [command]/usr/bin/git config --local --unset-all http.https://github.com/.extraheader
2026-05-04T03:56:10.8775414Z [command]/usr/bin/git submodule foreach --recursive sh -c "git config --local --name-only --get-regexp 'http\.https\:\/\/github\.com\/\.extraheader' && git config --local --unset-all 'http.https://github.com/.extraheader' || :"
2026-05-04T03:56:10.9040680Z [command]/usr/bin/git config --local --name-only --get-regexp ^includeIf\.gitdir:
2026-05-04T03:56:10.9075804Z [command]/usr/bin/git submodule foreach --recursive git config --local --show-origin --name-only --get-regexp remote.origin.url
2026-05-04T03:56:10.9456608Z Cleaning up orphan processes
2026-05-04T03:56:10.9735790Z ##[warning]Node.js 20 actions are deprecated. The following actions are running on Node.js 20 and may not work as expected: actions/checkout@v4, actions/setup-python@v5. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026. Node.js 20 will be removed from the runner on September 16th, 2026. Please check if updated versions of these actions are available that support Node.js 24. To opt into Node.js 24 now, set the FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true environment variable on the runner or in your workflow file. Once Node.js 24 becomes the default, you can temporarily opt out by setting ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true. For more information see: https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
