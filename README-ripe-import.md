RIPE DB data import
==========================
A set of tools to manage imports of ripe data into to the contact database.

The following input files are required:

* ripe.db.organisation.gz
* ripe.db.role.gz
* ripe.db.aut-num.gz
* ripe.db.inetnum.gz
* ripe.db.inet6num.gz
* delegated-ripencc-latest (only for --restrict-to-country)

The Tools `ripe_import` and `ripe_diff` will be searching for these files
in the current working directory by default.

The files can be downloaded
from the RIPE website (ftp://ftp.ripe.net/ripe/dbase/split/).

It is also possible to provide a whitelist of ASNs to load. Use the
``--asn-whitelist-file`` parameter to pass a filename. The script expects one
AS entry per line, with the AS-prefix, e.g. ``AS123``.

Configuration
=============

Parameters are resolved in the following priority order (highest first):

1. **Command-line arguments**
2. **`/etc/intelmq/contactdb-import.conf`**: optional JSON configuration
3. **`/etc/intelmq/contactdb-serve.conf`**: the contactdb webinterface configuration is read as a fallback for the database connection (`conninfo`)
4. **Built-in defaults**

The `--help` pages show the default values or the values from the configuration files if defined.

### contactdb-import.conf

The file is JSON-formatted.
Only the parameters you want to override need to be listed.
RIPE-specific file paths live under a `"ripe"` sub-object.
The example file `contactdb-import.conf.example` (in this repository) can be copied to `/etc/intelmq/contactdb-import.conf`.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `conninfo` | string | `"dbname=contactdb"` | libpq connection string |
| `verbose` | boolean | `false` | Enable verbose output |
| `ripe.organisation_file` | string | `"ripe.db.organisation.gz"` | Organisation data file |
| `ripe.role_file` | string | `"ripe.db.role.gz"` | Role data file |
| `ripe.asn_file` | string | `"ripe.db.aut-num.gz"` | AS number data file |
| `ripe.inetnum_file` | string | `"ripe.db.inetnum.gz"` | inetnum data file |
| `ripe.inet6num_file` | string | `"ripe.db.inet6num.gz"` | inet6num data file |
| `ripe.ripe_delegated_file` | string | `"delegated-ripencc-latest"` | Delegated file for country filtering |
| `asn_whitelist_file` | string | `""` | ASN whitelist file (empty = all ASNs) |
| `restrict_to_country` | list of strings | `null` | Country codes to restrict import to |

Example `/etc/intelmq/contactdb-import.conf`:
```json
{
    "conninfo": "...",
    "verbose": false,
    "ripe": {
        "organisation_file": "...",
        ...
    },
    "asn_whitelist_file": "...",
    "restrict_to_country": ["DE"]
}
```

Usually, only `restrict_to_country` is needed.
And `conninfo`, if it differs from the connection information for the fody webinterface.

Usage
=====

Download data to a directory using the script `ripe_download`, the program `curl` is required for this.

Call `ripe_import.py --help` or `ripe_diff.py --help`
to see all command line options.

The importer is capable of importing only entries which can be associated to a
CountryCode. This is supported natively for `inetnum` and `inetnum6` data
(IP-Data). For ASN an additional step is required, as the `autnum` datasets
(ASN-Data) do not provide this information. That is where the `delegated-list`
comes to play. In order to import only IP and ASN Data for one country, for
instance DE, use the following parameters: `--restrict-to-country DE` and
`--ripe-delegated-file delegated-ripencc-latest`.

Note: When providing an asn-whitelist file, the file specified with
`--ripe-delegated-file` and CountryCode based imports will be ignored for
ASN-Data. Only the ASN specified in the whitelist will be imported. IP-Data
will not be affected.

Now import the data into your ContactDB, we assume you used `contactdb` as
database name.

You can use `ripe_diff.py` instead of `ripe_import.py` below
to get shown what would be imported into the database by the import step
and which manual entries are related to the affected ASNs or networks.

**Make sure the connection to the database is made
with sufficient rights! Use the database superuser when in doubt.**


**Have enough RAM: reading in the database from 2021-02-12 needs
a little less than 8 GByte RAM, so system has to have more to keep running.**

The next step assumes you are currently in the same folder like the data you
downloaded.

```
cd $d
ripe_import.py --asn-whitelist-file=asn-DE.txt -v
```

If `conninfo` and `restrict_to_country` are set in
`/etc/intelmq/contactdb-import.conf`, no additional parameters are needed.

Here is a different example where the paths to the files are specified
explicitly:

```
ripe_import.py --conninfo "host=localhost dbname=contactdb" \
    --organisation-file=/tmp/ripe/ripe.db.organisation.gz \
    --role-file=/tmp/ripe/ripe.db.role.gz \
    --asn-file=/tmp/ripe/ripe.db.aut-num.gz \
    --ripe-delegated-file=/tmp/ripe/delegated-ripencc-latest \
    --restrict-to-country DE \
    --verbose
```

Also see the
[documentation of the libpg conninfo string](https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING).
The [documentation on environment variables](https://www.postgresql.org/docs/current/static/libpq-envars.html) to the connection also
points towards how to safely provide a password with a ~/.pgpass file.

### use as a module
`check-ripe.py` is a simple example how to use the module
`ripe_data` independently of intelmq to write a simple check
that operates on ripe's dbsplit datafiles. Capabilities and limitations
are documented with `ripe_data.py`.


### test data

For many tests is it okay to just use a subset of the inet[6?]num objects.
The following example limits the total lines and then an import uses
about 0.5 GByte RAM:
```sh
day=2021-03-03
cp --archive $day $day-trunc
cd $day-trunc
gzip -d --stdout ../$day/ripe.db.inet6num.gz | head --lines=300000 | gzip > ripe.db.inet6num.gz
gzip -d --stdout ../$day/ripe.db.inetnum.gz | head --lines=300000 | gzip > ripe.db.inetnum.gz
```
