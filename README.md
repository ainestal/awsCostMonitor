awsCostMonitor
==============

Get the live costs of the AWS objects.
This is a web application that allows you to fetch data from Amazon Web Services to see the current usage and the cost that this activity is generating.
It displays all the instances you have and the volumes attached to them getting the cost of all together.

Requeriments:
  To run the app:
- python >=2.7
- boto (https://github.com/boto/boto)
  Just to build the project:
- node.js >=0.10
- npm >=1.4.3
- yeoman


"Compiling" the code:
- Clone de repository
- Enter the folder where the code is
- Type:
    grunt build
- After the build is finished you can run the local server to browse the web application

Running the server:
- You need the .boto file with your credentials in your user folder
- Go to the folder where you cloned the code
- Type:
    python server.py


