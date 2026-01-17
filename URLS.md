
# project URLS Documentation

http://127.0.0.1:8000/api/
#==================================Authentication==================================#

POST                   role_name/register/                         → for Registration
example:- role_name= driver,owner
POST                  role_name/login/                             → for Login
POST                          /logout/                             → for Logout 
POST                     /change-password/                         → for Change passoword
POST                    /reset-password/                           → for Reset password

#====================================User Data======================================#

GET                         /User/                        → for User-List
POST                       /User/                         → for create user
GET BY ID                 /User/{id}/                     → for User-details 
PATCH                    /User/{id}/                      → for update user
DELETE                  /User/{id}/                       → for delete user

#====================================BIOMETRIC========================================#

GET                   /usersecurity/                      → for Usersecurity -List
POST                 /usersecurity/                       → for create Usersecurity
GET BY ID           /usersecurity/{user_id}/              → for Usersecurity-details
PATCH              /usersecurity/{user_id}/               → for  update  Usersecurity  
DELETE            /usersecurity/{user_id}/                → for delete Usersecurity

#=================================UPLOAD DOCUMENT=====================================#

GET                 /userdocuments/                       → for Upload Document-List
POST               /userdocuments/                        → for upload document
GET BY ID         /userdocuments/{user_id}/               → for upload document-details 
PATCH            /userdocuments/{user_id}/                → for update document
DELETE          /userdocuments/{user_id}/                 → for delete document

#===================================OTP Verification ==================================#

POST             /otp/send/                               → SEND OTP (MOBILE/EMAIL)
POST            /otp/verify/                              →  VERIFY OTP (MOBILE/EMAIL)
POST           /otp/resend/                               → RESEND OTP (MOBILE/EMAIL)
