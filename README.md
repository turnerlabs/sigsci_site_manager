# Signal Sciences Site Management Tool

## Prerequisites
This tool requires Python 3

## Installation

```shell
$ python3 setup.py install
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
usage: sigsci_site_manager list [-h]

optional arguments:
  -h, --help  show this help message and exit
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

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Identifying name of the site
  --display-name "Display Name", -N "Display Name"
                        Display name of the site
  --file FILENAME, -f FILENAME
                        Name of site file
  --dry-run             Print actions without making any changes
```

### Clone Command
```shell
$ sigsci_site_manager clone --help
usage: sigsci_site_manager clone [-h] --src SITE --dest SITE
                                 [--display-name "Display Name"] [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --src SITE, -s SITE   Site to clone from
  --dest SITE, -d SITE  Site to clone to
  --display-name "Display Name", -N "Display Name"
                        Display name of the new site
  --dry-run             Print actions without making any changes
```

### Merge Command
```shell
$ sigsci_site_manager merge --help
usage: sigsci_site_manager merge [-h] --dest SITE
                                 [--src SITE | --file FILENAME] [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --dest SITE, -d SITE  Site to merge onto
  --src SITE, -s SITE   Site to merge from
  --file FILENAME, -f FILENAME
                        Name of site file to merge from
  --dry-run             Print actions without making any changes
```