#!/usr/bin/expect

set timeout -1;
spawn /home/dqa/code/env/bin/python /home/dqa/data/pressure_test/manage.py changepassword admin;
expect {
    "Password:" { exp_send "password123\r" ; exp_continue }
    "Password (again):" { exp_send "password123\r" ; exp_continue }
    eof
}