Deploy BOINC applications
=========================

Deploy BOINC applications using the `AppVersionNew` [1] method.

### Requirements ###

* Requires `lxml`, which in turn requries `libxml2-dev`, `libxslt1-dev` Linux packages.

### Example usage ###

1. Change to the BOINC project user, and make sure `BOINC_PROJECT_DIR` environment variable is set.
2. Create a json file describing application details (named e.g., `app-deploy.json`):

    ```json
    {
	    "name": "muso",
	    "version": "1.20",
	    "platform": "i686-pc-linux-gnu",
	    "main_executable": "muso_i686-pc-linux-gnu"
    }
    ```
    `name`, `version` are application specific, `platform` is one of the definied platforms of BOINC. `main_executable` is the name of the file BOINC should execute to start the application.  

3. Run `app-deploy.py`:
    ```
    app-deploy.py --config ./app-deploy.json --source-dir ./app-files
    ```
    Where the folder `./app-files` contains the application files. If there is a previous deployment, `app-deploy.py` will refuse to run, and you have to remove files manually from the `apps/` folder. 

4. Add application to `project.xml`, if it is not there yet, e.g.:
    ```xml
    <boinc>
    ...
        <app>
            <name>muso</name>
            <user_friendly_name>Muso</user_friendly_name>
        </app>
    </boinc> 
    ```

5. Run `xadd` and `update_versions`.

### References ###

[1] https://boinc.berkeley.edu/trac/wiki/AppVersionNew
