# ISO Signal Sciences Site Management Tool

## Prequisites
This tool requires Python 3

## Installation

```shell
$ python3 setup.py install
```

## Usage

### Main Usage
```shell
$ sigsci_site_manager --help
usage: sigsci_site_manager [-h] --corp CORP --user USERNAME --token APITOKEN
                           {list,deploy,backup,clone} ...

Signal Sciences site management

optional arguments:
  -h, --help            show this help message and exit
  --corp CORP, -c CORP  Signal Sciences corp name
  --user USERNAME, -u USERNAME
                        Signal Sciences username
  --token APITOKEN, -t APITOKEN
                        Signal Sciences API token

Commands:
  {list,deploy,backup,clone}
    list                List sites
    deploy              Deploy a new site from a file
    backup              Backup a site to a file
    clone               Clone an existing site to a new site
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
usage: sigsci_site_manager deploy [-h] --name NAME --file FILENAME

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Site name
  --file FILENAME, -f FILENAME
                        Name of site file
```

### Clone Command
```shell
$ sigsci_site_manager clone --help
usage: sigsci_site_manager clone [-h] --src SITE --dest SITE

optional arguments:
  -h, --help            show this help message and exit
  --src SITE, -s SITE   Site to clone from
  --dest SITE, -d SITE  Site to clone to
```
