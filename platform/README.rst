Case Conductor Platform
=======================

Documentation of setup (Tested on Ubuntu 10.10 desktop, 10.04 server, and
Mac OS X).  Assumes $CCPLATFORM is the directory containing this README file
and ``tcm.war``.

Download and unzip jBoss 5.1::

    $ wget -O jboss-5.1.0.GA.zip http://sourceforge.net/projects/jboss/files/JBoss/JBoss-5.1.0.GA/jboss-5.1.0.GA.zip/download
    $ unzip jboss-5.1.GA.zip

Copy the .war file in::

    $ cp $CCPLATFORM/tcm.war jboss-5.1.0.GA/server/default/deploy/

Add the MySQL connector jar and the datasource configuration into jBoss::

    $ cp $CCPLATFORM/deploy-config/mysql-connector-java-5.1.12.jar jboss-5.1.0.GA/server/default/lib/
    $ cp $CCPLATFORM/deploy-config/utest-ds.xml jboss-5.1.0.GA/server/default/deploy/

Edit the copied utest-ds.xml file (the one under
``jboss-5.1.0.GA/server/default/deploy/utest-ds.xml``) to set the name of your
MySQL database (default is ``tcm``) and your MySQL user and password (defaults
to ``root`` with no password).

Note that the platform currently does not support MySQL 5.5 -- some operations
will fail with foreign key constraint violations. MySQL 5.1 must be used.

Create your MySQL database schema (you may need to use the ``-u`` option to the
commands here if you are using a database user other than your current shell
user, and you'll need to substitute a different db name if not using ``tcm``)::

    $ mysqladmin create tcm
    $ mysql tcm < $CCPLATFORM/db_scripts/db_tcm_create_empty_db_script.sql

You'll need to also execute each database update script in that same directory, in order. For example::

    $ mysql tcm < $CCPLATFORM/db_scripts/db_tcm_update_db_script_1.sql

The shell script ``reset-mysql.sh`` automates dropping an existing database if
it exists, creating the database, setting up the initial schema and running all
update scripts. (If you are using a database name other than ``tcm`` and/or a
database user other than ``root``, you'll need to run this script as
``./reset-mysql.sh database_name user_name``).

And run the server::

    $ jboss-5.1.0.GA/bin/run.sh

Give it a minute or two to start up - when it's ready you'll see a line in its console output that looks like this::

    17:50:59,453 INFO  [ServerImpl] JBoss (Microcontainer) [5.1.0.GA (build: SVNTag=JBoss_5_1_0_GA date=200905221053)] Started in 48s:247ms

Now you should be able to connect to http://localhost:8080/tcm/services/ and
see the web-service WADL file links listed, and connect to
e.g. http://localhost:8080/tcm/services/v2/rest/companies/ and see the list of
companies.

Future Updates
--------------

If you upgrade your copy of ``caseconductor-ui`` and the ``tcm.war`` file
has changed, you'll need to copy in the updated one::

    $ cp $CCPLATFORM/tcm.war jboss-5.1.0.GA/server/default/deploy/

If any new database update scripts were included in the platform update,
you'll need to run them, e.g.::

    $ mysql -uroot < $CCPLATFORM/db_scripts/db_tcm_update_db_script_29.sql

Alternatively, you can just run ``reset-mysql.sh`` again, if you don't mind
losing any data in your local database and starting over with a fresh database.
