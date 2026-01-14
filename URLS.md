# project URLS Documentation
#==================================Authentication==================================#

POST                   /api/register/                         → for Registration
POST                  /api/login/                             → for Login
POST                 /api/logout/                             → for Logout 
POST                /change-password/                         → for Change passoword
POST               /reset-password/                           → for Reset password

#====================================User Data======================================#

GET                         /api/User/                        → for User-List
POST                       /api/User/                         → for create user
GET BY ID                 /api/User/{id}/                     → for User-details 
PATCH                    /api/User/{id}/                      → for update user
DELETE                  /api/User/{id}/                       → for delete user

#====================================BIOMETRIC========================================#

GET                   /api/usersecurity/                      → for Usersecurity -List
POST                 /api/usersecurity/                       → for create Usersecurity
GET BY ID           /api/usersecurity/{user_id}/              → for Usersecurity-details
PATCH              /api/usersecurity/{user_id}/               → for  update  Usersecurity  
DELETE            /api/usersecurity/{user_id}/                → for delete Usersecurity

#=================================UPLOAD DOCUMENT=====================================#

GET                 /api/userdocuments/                       → for Upload Document-List
POST               /api/userdocuments/                        → for upload document
GET BY ID         /api/userdocuments/{user_id}/               → for upload document-details 
PATCH            /api/userdocuments/{user_id}/                → for update document
DELETE          /api/userdocuments/{user_id}/                 → for delete document

#===================================OTP Verification ==================================#

POST             /api/otp/send/                               → SEND OTP (MOBILE/EMAIL)
POST            /api/otp/verify/                              →  VERIFY OTP (MOBILE/EMAIL)
POST           /otp/api/resend/                               → RESEND OTP (MOBILE/EMAIL)
