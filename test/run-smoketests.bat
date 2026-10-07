@echo off
setlocal enabledelayedexpansion

set "MODE=%~1"
if "%MODE%"=="" set "MODE=upsert"
if /I "%MODE%"=="--delete" set "MODE=delete"
if /I "%MODE%"=="cleanup" set "MODE=delete"
if /I "%MODE%"=="help" set "MODE=help"
if /I "%MODE%"=="-h" set "MODE=help"

if "%MODE%"=="help" (
  echo Usage: run-smoketests.bat [upsert^|delete^|cleanup]
  exit /b 0
)

if /I not "%MODE%"=="upsert" if /I not "%MODE%"=="delete" (
  echo Unknown mode: %MODE%
  echo Usage: run-smoketests.bat [upsert^|delete^|cleanup]
  exit /b 1
)

set "BASE_URL=%BASE_URL%"
if "%BASE_URL%"=="" set "BASE_URL=http://localhost:8080/fhir"

set "FILES[0]=%~dp0smoketest\01-organization.json"
set "FILES[1]=%~dp0smoketest\02-practitioner.json"
set "FILES[2]=%~dp0smoketest\03-patient.json"
set "FILES[3]=%~dp0smoketest\04-relatedperson.json"
set "FILES[4]=%~dp0smoketest\05-coverage.json"
set "FILES[5]=%~dp0smoketest\06-encounter.json"
set "FILES[6]=%~dp0smoketest\07-condition.json"
set "FILES[7]=%~dp0smoketest\08-observation.json"

if /I "%MODE%"=="delete" (
  for /L %%i in (7,-1,0) do (
    set "file=!FILES[%%i]!"
    if not exist "!file!" (
      echo Missing required smoke file: !file!
      exit /b 1
    )

    for /f "delims=" %%R in ('powershell -NoProfile -Command "$j = Get-Content -Raw '!file!'; $obj = $j | ConvertFrom-Json; $obj.resourceType"') do set "RESOURCE_TYPE=%%R"
    for /f "delims=" %%R in ('powershell -NoProfile -Command "$j = Get-Content -Raw '!file!'; $obj = $j | ConvertFrom-Json; $obj.id"') do set "RESOURCE_ID=%%R"
    if not defined RESOURCE_TYPE (
      echo Unable to determine resourceType from !file!
      exit /b 1
    )
    if not defined RESOURCE_ID (
      echo Unable to determine resource id from !file!
      exit /b 1
    )

    echo Deleting !file! as !RESOURCE_TYPE!/!RESOURCE_ID! from %BASE_URL%
    curl -sS -X DELETE "%BASE_URL%/!RESOURCE_TYPE!/!RESOURCE_ID!"
    echo.
    echo ----------------------------------------
    echo.
  )
  exit /b 0
)

for /L %%i in (0,1,7) do (
  set "file=!FILES[%%i]!"
  if not exist "!file!" (
    echo Missing required smoke file: !file!
    exit /b 1
  )

  for /f "delims=" %%R in ('powershell -NoProfile -Command "$j = Get-Content -Raw '!file!'; $obj = $j | ConvertFrom-Json; $obj.resourceType"') do set "RESOURCE_TYPE=%%R"
  for /f "delims=" %%R in ('powershell -NoProfile -Command "$j = Get-Content -Raw '!file!'; $obj = $j | ConvertFrom-Json; $obj.id"') do set "RESOURCE_ID=%%R"
  if not defined RESOURCE_TYPE (
    echo Unable to determine resourceType from !file!
    exit /b 1
  )
  if not defined RESOURCE_ID (
    echo Unable to determine resource id from !file!
    exit /b 1
  )

  echo Running !file! as !RESOURCE_TYPE!/!RESOURCE_ID! against %BASE_URL%
  curl -sS -X PUT "%BASE_URL%/!RESOURCE_TYPE!/!RESOURCE_ID!" -H "Content-Type: application/fhir+json" --data-binary "@!file!"
  echo.
  echo ----------------------------------------
  echo.
)
