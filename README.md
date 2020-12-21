# How one can access ISO 10303 Repository
# Python client

EDMtruePLM web application has some REST web services exposed.
This is Python client script that demonstrates basic usage of the services.

The project consists of the following two parts.
1. Client stub generated by [swagger-codegen](https://github.com/swagger-api/swagger-codegen)
2. Small client script.

## User credentials

File ***democli.properties*** has dummy user credentials.
Please, ask Jotne to provide user credentials for you.

## How to build

1. Clone source files from the GitHub repository
```javascript
git clone https://github.com/Deruga/kyklos_python.git .
```

2. Download swagger-codegen
This can be done via PowerShell command in Windows. Run PowerShell and execute the following command.
Please, get appropriate version

```javascript
Invoke-WebRequest -Uri https://repo1.maven.org/maven2/io/swagger/swagger-codegen-cli/2.4.17/swagger-codegen-cli-2.4.17.jar -OutFile swagger-codegen-cli.jar
```

3. Assume ***swagger-codegen-cli.jar*** is already downloaded into root folder of your working copy.
Run python-generate.bat script to generate client stub (***demolib*** library project)

```javascript
python-generate.bat
```

4. Install generated ***demolib*** python library

```javascript
pip install demolib
```

5. Script ***democli.py*** can be imported to appropriate IDE that supports Python development.
IDE allows you to debug the client script.

The simplest way to run the script is the following


```javascript
python democli.py
```
