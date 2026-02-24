@echo off
echo Activating Virtual Environment...
call "%~dp0venv\Scripts\activate.bat"

echo.
echo Running TC001...
python "%~dp0testsprite_tests\TC001_authentication_login_post_with_valid_and_invalid_credentials.py"

echo.
echo Running TC002...
python "%~dp0testsprite_tests\TC002_book_management_get_book_detail_valid_and_invalid_id.py"

echo.
echo Running TC003...
python "%~dp0testsprite_tests\TC003_book_transactions_post_request_book_with_and_without_authentication.py"

echo.
echo Running TC004...
python "%~dp0testsprite_tests\TC004_dashboard_api_get_overall_library_statistics_with_and_without_authentication.py"

echo.
echo Running TC005...
python "%~dp0testsprite_tests\TC005_departmental_browse_get_department_books_valid_and_invalid_department.py"

echo.
echo Running TC006...
python "%~dp0testsprite_tests\TC006_library_services_post_ask_librarian_with_valid_and_invalid_data.py"

echo.
echo All tests completed.
pause
