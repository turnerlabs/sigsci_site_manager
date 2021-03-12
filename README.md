# Signal Sciences Site Management Tool

[![](https://img.shields.io/pypi/v/sigsci_site_manager.svg)](https://pypi.org/project/sigsci-site-manager/)
![](https://img.shields.io/pypi/pyversions/sigsci_site_manager.svg)
![](https://img.shields.io/pypi/format/sigsci_site_manager.svg)
![](https://img.shields.io/github/license/turnerlabs/sigsci_site_manager.svg)

## Installation

```shell
$ pip3 install sigsci_site_manager
```

## Usage

### Main Usage
```shell
$ sigsci_site_manager --help
usage: sigsci_site_manager [-h] [--corp CORP] [--user [USERNAME]]
                           [--password [PASSWORD] | --token [APITOKEN]]
                           {list,deploy,backup,clone} ...

Signal Sciences site management

optional arguments:
  -h, --help            show this help message and exit
  --corp CORP, -c CORP  Signal Sciences corp name. If omitted will try to use
                        value in $SIGSCI_CORP.
  --user [USERNAME], -u [USERNAME]
                        Signal Sciences username. If omitted will try to use
                        value in $SIGSCI_EMAIL.
  --password [PASSWORD], -p [PASSWORD]
                        Signal Sciences password. If omitted will try to use
                        value in $SIGSCI_PASSWORD
  --token [APITOKEN], -t [APITOKEN]
                        Signal Sciences API token. If omitted will try to use
                        value in $SIGSCI_API_TOKEN

Commands:
  {list,deploy,backup,clone,merge}
    list                List sites
    deploy              Deploy a new site from a file
    backup              Backup a site to a file
    clone               Clone an existing site to a new site
    merge               Merge a site onto another
```
 
### List Command
```shell
$ sigsci_site_manager list --help
usage: sigsci_site_manager list [-h] [--filter PATTERN]

optional arguments:
  -h, --help  show this help message and exit
  --filter PATTERN  Filter site names using a wildcard pattern
```

### Backup Command
```shell
$ sigsci_site_manager backup --help
usage: sigsci_site_manager backup [-h] --name NAME --out FILENAME

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Site name
  --out FILENAME, -o FILENAME
                        File to save backup to
```

### Deploy Command
```shell
$ sigsci_site_manager deploy --help
usage: sigsci_site_manager deploy [-h] --name NAME
                                  [--display-name "Display Name"] --file
                                  FILENAME [--dry-run]
                                  [--include CATEGORY_LIST | --exclude CATEGORY_LIST]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Identifying name of the site
  --display-name "Display Name", -N "Display Name"
                        Display name of the site
  --file FILENAME, -f FILENAME
                        Name of site file
  --dry-run             Print actions without making any changes
  --include CATEGORY_LIST
                        CSV list of categories to include in the merge.
                        Options: RULE_LISTS, CUSTOM_SIGNALS, REQUEST_RULES,
                        SIGNAL_RULES, TEMPLATED_RULES, CUSTOM_ALERTS,
                        SITE_MEMBERS, INTEGRATIONS, ADVANCED_RULES
  --exclude CATEGORY_LIST
                        CSV list of categories to exclude in the merge.
                        Options: RULE_LISTS, CUSTOM_SIGNALS, REQUEST_RULES,
                        SIGNAL_RULES, TEMPLATED_RULES, CUSTOM_ALERTS,
                        SITE_MEMBERS, INTEGRATIONS, ADVANCED_RULES
```

### Clone Command
```shell
$ sigsci_site_manager clone --help
usage: sigsci_site_manager clone [-h] --src SITE --dest SITE
                                 [--display-name "Display Name"] [--dry-run]
                                 [--include CATEGORY_LIST | --exclude CATEGORY_LIST]

optional arguments:
  -h, --help            show this help message and exit
  --src SITE, -s SITE   Site to clone from
  --dest SITE, -d SITE  Site to clone to
  --display-name "Display Name", -N "Display Name"
                        Display name of the new site
  --dry-run             Print actions without making any changes
  --include CATEGORY_LIST
                        CSV list of categories to include in the merge.
                        Options: RULE_LISTS, CUSTOM_SIGNALS, REQUEST_RULES,
                        SIGNAL_RULES, TEMPLATED_RULES, CUSTOM_ALERTS,
                        SITE_MEMBERS, INTEGRATIONS, ADVANCED_RULES
  --exclude CATEGORY_LIST
                        CSV list of categories to exclude in the merge.
                        Options: RULE_LISTS, CUSTOM_SIGNALS, REQUEST_RULES,
                        SIGNAL_RULES, TEMPLATED_RULES, CUSTOM_ALERTS,
                        SITE_MEMBERS, INTEGRATIONS, ADVANCED_RULES
```

### Merge Command
```shell
$ sigsci_site_manager merge --help
usage: sigsci_site_manager merge [-h] --dest SITE
                                 [--src SITE | --file FILENAME] [--dry-run]
                                 [--include CATEGORY_LIST | --exclude CATEGORY_LIST]
                                 [--yes]

optional arguments:
  -h, --help            show this help message and exit
  --dest SITE, -d SITE  Site to merge onto (accepts wildcard pattern)
  --src SITE, -s SITE   Site to merge from
  --file FILENAME, -f FILENAME
                        Name of site file to merge from
  --dry-run             Print actions without making any changes
  --include CATEGORY_LIST
                        CSV list of categories to include in the merge.
                        Options: RULE_LISTS, CUSTOM_SIGNALS, REQUEST_RULES,
                        SIGNAL_RULES, TEMPLATED_RULES, CUSTOM_ALERTS,
                        SITE_MEMBERS, INTEGRATIONS, ADVANCED_RULES
  --exclude CATEGORY_LIST
                        CSV list of categories to exclude in the merge.
                        Options: RULE_LISTS, CUSTOM_SIGNALS, REQUEST_RULES,
                        SIGNAL_RULES, TEMPLATED_RULES, CUSTOM_ALERTS,
                        SITE_MEMBERS, INTEGRATIONS, ADVANCED_RULES
  --yes, -y             Automatic yes to prompts
```

### User Command
```shell
$ sigsci_site_manager user --help
usage: sigsci_site_manager user [-h] [--site SITE] [--dry-run]
                         {add,list,member,remove} ...

optional arguments:
  -h, --help            show this help message and exit
  --site SITE, -s SITE  Name of site
  --dry-run             Print actions without making any changes

Manage User Command:
  {add,list,member,remove}
    add                 Add user to corp, or to site if site is specified
    list                List users in corp, or in site if site is specified
    member              list user site/role membership
    remove              remove user from corp/site
```

### User add SubCommand
```shell
$ sigsci_site_manager user add --help
usage: sigsci_site_manager user add [-h] [--id EMAIL_ID | --file FILENAME]
                             [--role {admin,user,observer,owner}] 
                             [--override]

optional arguments:
  -h, --help            show this help message and exit
  --id EMAIL_ID, -i EMAIL_ID
                        User to add to site
  --file FILENAME, -f FILENAME
                        Path to file containing email_id,role pair one per
                        line. Adds each user to site if site is specified,
                        otherwise adds user from the corp org. Use - to read
                        input from stdin

add user:
  --role {admin,user,observer,owner}, -r {admin,user,observer,owner}
                        Role to assign user in site. Default role is observer
  --api-user, -a        Enable as api user. Enables user for api access
```

### User list Subcommand
```shell
$ sigsci_site_manager user list --help
usage: sigsci_site_manager user list [-h]

optional arguments:
  -h, --help  show this help message and exit
```

### User member Subcommand
```shell
$ sigsci_site_manager user member --help
usage: sigsci_site_manager user member [-h] --id EMAIL_ID

optional arguments:
  -h, --help            show this help message and exit

list user site/role membership:
  --id EMAIL_ID, -i EMAIL_ID
                        Email id for the user to examine site/corp membership.
```

### User remove Subcommand
```shell
$ sigsci_site_manager user remove  --help
usage: sigsci_site_manager user remove [-h] [--id EMAIL_ID | --file FILENAME]

optional arguments:
  -h, --help            show this help message and exit
  --id EMAIL_ID, -i EMAIL_ID
                        Email id for the user to delete. Deletes user from
                        site if site is specified, otherwise deletes user from
                        the system
  --file FILENAME, -f FILENAME
                        Path to file containing, email_id one per line.Deletes
                        user from site if site is specified, otherwise deletes
                        user from the system. Use - to read input from stdin
```
### Validate Command
```shell
$ sigsci_site_manager validate --help
usage: sigsci_site_manager validate [-h] --name NAME --target URL [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Site name
  --target URL, -d URL  URL to test against
  --dry-run             Print actions without making any changes
  ```
### Migrate Command
```shell
$ sigsci_site_manager migrate --help
usage: sigsci_site_manager migrate [-h] --dest-corp DESTCORP --file FILENAME
                                   [--out OUTPUTFILE] [--strip STRIP]
                                   [--migrate-users]

optional arguments:
  -h, --help            show this help message and exit
  --dest-corp DESTCORP, -d DESTCORP
                        Destination corp to migrate to
  --file FILENAME, -f FILENAME
                        Filename of to migrate
  --out OUTPUTFILE, -o OUTPUTFILE
                        File to save migrated backup to, defaults to
                        "migrated_<backup filename>"
  --strip STRIP, -s STRIP
                        Strip all items with corp dependencies from the
                        migrated backup
  --migrate-users, -u   Preserve users in migrated backup
  ```
