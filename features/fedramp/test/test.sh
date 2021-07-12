#!/bin/sh
######## BANNER ################
BANNER=$(cat /etc/issue.net | grep "You are accessing a U.S. Government")
if [ -z "$BANNER" ]
then
      echo "${red}BANNER failed${reset}"
else
      echo "${green}BANNER passed${reset}"
fi
######## SSH ################
SSH_MAX_CLIENT=$(cat /etc/ssh/sshd_config | grep -i "^ClientAliveCountMax")
if [ -z "$SSH_MAX_CLIENT" ]
then
      echo "${red}SSH_MAX_CLIENT failed${reset}"
else
      echo "${green}SSH_MAX_CLIENT passed${reset}"
fi
SSH_MAX_CLIENT_INTERVAL=$(cat /etc/ssh/sshd_config | grep -i "^ClientAliveInterval")
if [ -z "$SSH_MAX_CLIENT_INTERVAL" ]
then
      echo "${red}SSH_MAX_CLIENT_INTERVAL failed${reset}"
else
      echo "${green}SSH_MAX_CLIENT_INTERVAL passed${reset}"
fi
SSH_PERMIT_ROOT_LOGIN=$(cat /etc/ssh/sshd_config | grep -i "^PermitRootLogin" | grep -i "no")
if [ -z "$SSH_PERMIT_ROOT_LOGIN" ]
then
      echo "${red}SSH_PERMIT_ROOT_LOGIN failed${reset}"
else
      echo "${green}SSH_PERMIT_ROOT_LOGIN passed${reset}"
fi
SSH_PERMIT_EMPTY_PWD=$(cat /etc/ssh/sshd_config | grep -i "^PermitEmptyPasswords" | grep -i "no")
if [ -z "$SSH_PERMIT_EMPTY_PWD" ]
then
      echo "${red}SSH_PERMIT_EMPTY_PWD failed${reset}"
else
      echo "${green}SSH_PERMIT_EMPTY_PWD passed${reset}"
fi
######## PAM ################
PAM_PASSWORD_REQUIRED=$(cat /etc/pam.d/common-password | grep -i "^password*required*pam_permit.so")
if [ -z "$SSH_MAX_CLIENT" ]
then
      echo "${red}PAM_PASSWORD_REQUIRED failed${reset}"
else
      echo "${green}PAM_PASSWORD_REQUIRED passed${reset}"
fi
PAM_PASSWORD_REQUISITE=$(cat /etc/pam.d/common-password | grep -i "^password*requisite*pam_permit.so")
if [ -z "$SSH_MAX_CLIENT" ]
then
      echo "${red}PAM_PASSWORD_REQUISITE failed${reset}"
else
      echo "${green}PAM_PASSWORD_REQUISITE passed${reset}"
fi
PAM_COMMON_AUTH=$(cat /etc/pam.d/common-auth | grep -i "pam_fail")
if [ -z "$PAM_COMMON_AUTH" ]
then
      echo "${red}PAM_COMMON_AUTH failed${reset}"
else
      echo "${green}PAM_COMMON_AUTH passed${reset}"
fi
######## CHRONY ################
CHRONY=$(chronyc sourcestats -v | grep -i "169.254.169.123")
if [ -z "$CHRONY" ]
then
      echo "${red}CHRONY failed${reset}"
else
      echo "${green}CHRONY passed${reset}"
fi
######## AUDIT ################
AUDIT_RULES=$(sudo cat /etc/audit/audit.rules | grep -i "/var/log/tallylog")
if [ -z "$AUDIT_RULES" ]
then
      echo "${red}AUDIT_RULES failed${reset}"
else
      echo "${green}AUDIT_RULES passed${reset}"
fi
AUDIT_CONF=$(sudo cat /etc/audit/auditd.conf | grep -i "^krb5_principal")
if [ -z "$AUDIT_CONF" ]
then
      echo "${red}AUDIT_CONF failed${reset}"
else
      echo "${green}AUDIT_CONF passed${reset}"
fi
######## AIDE ################
AIDE_CONF=$(sudo cat /etc/aide/aide.conf | grep -i "^/var/log/faillog")
if [ -z "$AIDE_CONF" ]
then
      echo "${red}AIDE_CONF failed${reset}"
else
      echo "${green}AIDE_CONF passed${reset}"
fi
# Cloud watch agent is irrelevant on Gardener AMIs as we push logs via fluentd.
######## CLOUDWATCH ############
# CLOUDWATCH_DS=$(sudo docker ps | grep -i "cloudwatch")
# if [ -z "$CLOUDWATCH_DS" ]
# then
#   CLOUDWATCH_CONFIG=$(sudo cat /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json | grep -i "/var/log/syslog")
#   if [ -z "$CLOUDWATCH_CONFIG" ]
#   then
#       echo "${red}CLOUDWATCH_CONFIG failed${reset}"
#   else
#       echo "${green}CLOUDWATCH_CONFIG passed${reset}"
#   fi
#   CLOUDWATCH_SERVICE=$(systemctl --type=service --state=active | grep -i "amazon-cloudwatch-agent")
#   if [ -z "$CLOUDWATCH_SERVICE" ]
#   then
#       echo "${red}CLOUDWATCH_SERVICE failed${reset}"
#   else
#       echo "${green}CLOUDWATCH_SERVICE passed${reset}"
#   fi
# else
#       echo "${green}CLOUDWATCH_DAEMONSET passed${reset}"
# fi
######## APPARMOR ############
APPARMOR_STATUS=$(sudo aa-status | grep -i "apparmor module is loaded")
if [ -z "$APPARMOR_STATUS" ]
then
      echo "${red}APPARMOR_STATUS failed${reset}"
else
      echo "${green}APPARMOR_STATUS passed${reset}"
fi
APPARMOR_SERVICE=$(systemctl --type=service --state=active | grep -i "apparmor")
if [ -z "$APPARMOR_SERVICE" ]
then
      echo "${red}APPARMOR_SERVICE failed${reset}"
else
      echo "${green}APPARMOR_SERVICE passed${reset}"
fi
######## LIMITS ############
LIMITS_CONFIG=$(cat /etc/security/limits.conf  | grep -i "^*" | grep -i maxlogins)
if [ -z "$LIMITS_CONFIG" ]
then
      echo "${red}LIMITS_CONFIG failed${reset}"
else
      echo "${green}LIMITS_CONFIG passed${reset}"
fi
######## CRONTAB ############
CRONTAB_AIDE=$(sudo crontab -l  | grep -i "aide")
if [ -z "$CRONTAB_AIDE" ]
then
      echo "${red}CRONTAB_AIDE failed${reset}"
else
      echo "${green}CRONTAB_AIDE passed${reset}"
fi
CRONTAB_CLAMAV=$(sudo crontab -l  | grep -i "clamav")
if [ -z "$CRONTAB_CLAMAV" ]
then
      echo "${red}CRONTAB_CLAMAV failed${reset}"
else
      echo "${green}CRONTAB_CLAMAV passed${reset}"
fi
# This test is not relevant because it the Ansible install of clamav doesn't use a daemon.
# ######## CLAMAV ################
# CLAMAV_CONF=$(sudo cat /etc/clamav/clamd.conf | grep -i "^ScanSWF")
# if [ -z "$CLAMAV_CONF" ]
# then
#       echo "${red}CLAMAV_CONF failed${reset}"
# else
#       echo "${green}CLAMAV_CONF passed${reset}"
# fi
######## KERNEL ################
KERNEL_RANDOM=$(cat /proc/sys/kernel/randomize_va_space | grep -i "2")
if [ -z "$KERNEL_RANDOM" ]
then
      echo "${red}KERNEL_RANDOM failed${reset}"
else
      echo "${green}KERNEL_RANDOM passed${reset}"
fi
KERNEL_FIPS=$(sudo cat /proc/sys/crypto/fips_enabled | grep -i "1")
KF=$(sudo cat /proc/sys/crypto/fips_enabled)
if [ -z "$KERNEL_FIPS" ]
then
      echo "${red}KERNEL_FIPS failed${reset}"
      echo "Printing out result of TEST: 
      $KF"
else
      echo "${green}KERNEL_FIPS passed${reset}"
fi
KERNEL_CIPHERS=$(/usr/bin/openssl ciphers -v | grep -i "AES256-SHA")
KC=$(/usr/bin/openssl ciphers -v)
if [ -z "$KERNEL_CIPHERS" ]
then
      echo "${red}KERNEL_CIPHERS failed${reset}"
      echo "Printing out result of TEST:
      $KC"
else
      echo "${green}KERNEL_CIPHERS passed${reset}"
fi
######## IPTABLES ################
IPTABLES_CONFIG=$(sudo iptables -n -L -v --line-numbers | grep -i "0.0.0.0/0")
if [ -z "$IPTABLES_CONFIG" ]
then
      echo "${red}IPTABLES_CONFIG failed${reset}"
else
      echo "${green}IPTABLES_CONFIG passed${reset}"
fi
######## SYSTEM ################
SYSTEM_LOGINS=$(cat /etc/login.defs | grep -i "^PASS_MAX_DAYS")
if [ -z "$SYSTEM_LOGINS" ]
then
      echo "${red}SYSTEM_LOGINS failed${reset}"
else
      echo "${green}SYSTEM_LOGINS passed${reset}"
fi
