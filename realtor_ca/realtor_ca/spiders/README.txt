

# # curl "http://3.80.86.46.54:6800/schedule.json" -d project=vlive -d spider=duproprio -d setting="FEED_URI=/home/ubuntu/vlive/vlive/vlive.csv
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=duproprio -d spider=kijiji -d spider=lespac -d spider=publimaison -d spider=logisqc
# # curl http://3.80.86.46.54:6800/listprojects.json
# # curl http://3.80.86.46.54:6800/listspiders.json?project=vlive
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=duproprio -d spider=kijiji -d spider=lespac -d spider=publimaison -d spider=logisqc

# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=centris
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=duproprio
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=kijiji
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=lespac
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=publimaison
# # curl http://3.80.86.46.54:6800/schedule.json -d project=vlive -d spider=logisqc


# # username_mongo = EC2_1
# # password_mongo = 2R0A62570nN0Xk97

# # ssh -i "C:\Users\momie\Downloads\scrapy-vlive.pem" ec2-user@3.80.86.46.54   commande pour de connecter au terminal EC2
# # source scrapyd-env/bin/activate
# # scp -i "C:\Users\momie\Downloads\scrapy-vlive.pem" -r D:\web_scraping\envs\V_RADAR\vlive ec2-user@3.80.86.46.54:/home/ec2-user/
# # ssh -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@54.90.65.46 
# # """ssh -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@54.90.65.46 """ # commande pour de connecter au terminal EC2 Vlive-Canada-Qc-Launch
# # """ssh -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" ec2-user@204.236.196.236 """ # commande pour de connecter au terminal EC2 Vlive-Canada-Qc-Launch
# # '''scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@204.236.196.236:/home/ec2-user/'''
# # '''scp -i C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem ec2-user@204.236.196.236:/home/ec2-user/'''
# # '''scp -i C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem ec2-user@204.236.196.236:/home/ec2-user/'''
# # '''scp -i C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem ec2-user@204.236.196.236:/home/ec2-user/'''
# # '''scp -i C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem ec2-user@204.236.196.236:/home/ec2-user/'''
# # scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" ec2-user@204.236.196.236:/home/ec2-user/
# # scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@204.236.196.236:/home/ec2-user/
# # scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@204.236.196.236:/home/ec2-user/
# # scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@204.236.196.236:/home/ec2-user/

# # scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" "C:\Users\momie\Downloads\Vlive-Canada-Qc-Scrapyd_1.pem" ec2-user@204.236.196.236:/home/ec2-user/
# # rm /home/ec2-user/Vlive-Canada-Qc-Launch.pem

# # """ssh -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" ec2-user@204.236.196.236 """ # Se connecter au terminal EC2 Vlive-Canada-Qc-Master 
# # """sudo su""" # Se connecter en tant qu'utilisateur root 
# # '''apt install python3 python3-pip -y''' # Installer python3 et pip3
# # '''pip3 install virtualenv''' # Installer virtualenv
# # '''mkdir myenv''' # Créez un répertoire pour votre environnement virtuel 
# # '''cd myenv''' # Accédez au répertoire de l'environnement virtuel 
# # '''virtualenv myenv''' # Créez un environnement virtuel
# # '''source myenv/bin/activate''' # Activez l'environnement virtuel
# # scrapyd-deploy -p vlive -u http://204.236.196.236:6800/
# # scrapyd-deploy Vlive-Canada-Qc-Master -p vlive

# # '''Déployer mon projet scrapy sur EC2'''
# # # scp -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" -r "D:\web_scraping\envs\V_RADAR\vlive" ec2-user@204.236.196.236:/tmp/
# # # ssh -i "C:\Users\momie\Downloads\Vlive-Canada-Qc-Launch.pem" ec2-user@204.236.196.236
# # '''sudo mv /tmp/vlive /home/ec2-user/myenv/''' # Pour déplacer le répertoire "vlive" du répertoire /tmp/ vers /home/ec2-user/myenv/


# # # ---------------------------------------------------------------------------------------------------------------------------------------
# # '''tar -czvf vlive.tar.gz vlive''' # créer un fichier tar du projet
# # '''zip -r vlive.zip vlive''' # créer un fichier compressé pour exporter le projet sur EC2
# # '''scp -i "EC2_Master.pem" vlive.tar.gz ec2-user@3.80.86.46.54:/tmp/''' # exporter le projet sur EC2
# # # ---------------------------------------------------------------------------------------------------------------------------------------
# # """Après le transfert, connectez-vous à votre instance EC2 via SSH et extrayez le contenu du fichier compressé à l'emplacement souhaité"""
# # # cd /home/ec2-user/myenv/
# # # tar -xzvf /tmp/vlive.tar.gz
# # # ---------------------------------------------------------------------------------------------------------------------------------------

ssh -i C:\Users\momie\Downloads\EC2_Master.pem ec2-user@3.80.86.46 | # Se connecter au terminal EC2 Vlive-Canada-Qc-Master
scp -i "C:\Users\momie\Downloads\EC2_Master.pem" vlive.tar.gz ec2-user@3.80.86.46.54:/tmp/ | # exporter le projet sur EC2
tar -xzvf /tmp/vlive.tar.gz -C /home/ec2-user/myenv/ | # extraire le contenu du fichier compressé à l'emplacement souhaité

# # -------------------------------------------------Créer un environnement virtuel -------------------------------------------------- #
# '''ssh -i "C:\Users\momie\Downloads\EC2_Master.pem" ec2-user@3.80.86.46.54''' # Connectez-vous à votre instance EC2 via SSH
#======================================================================================================================================#
# ------------- Mettre à jour les packages de l'instance | # Installer Python 3 et pip | # Installer virtualenv ------------- #
sudo yum update -y  
sudo yum install python3 python3-pip -y  
sudo pip3 install virtualenv  
# ------------- Mettre à jour les packages de l'instance | # Installer Python 3 et pip | # Installer virtualenv ------------- #
#======================================================================================================================================#
# # -------------------------------------------------Créer un environnement virtuel -------------------------------------------------- #
# '''mkdir myenv''' # Créez un répertoire pour votre environnement virtuel
# '''cd myenv'''  # Accédez au répertoire de l'environnement virtuel
# '''virtualenv myenv'''  # Créez un environnement virtuel
# '''source WebScraping/bin/activate'''  # Activez l'environnement virtuel
# '''deactivate''' # Désactiver l'environnement virtuel
# # -------------------------------------------------Créer un environnement virtuel -------------------------------------------------- #

ssh -i C:\Users\momie\Downloads\EC2_Master.pem ec2-user@3.80.86.46
scrapyd-client deploy VLive_Canada_Qc_Master -p vlive
curl "http://3.80.86.46:6800/listversions.json?project=vlive?spider=centris"
curl "http://3.80.86.46.54:6800/shedule.json" -d vlive -d spider=centris
curl "http://3.80.86.46.54:6800/shedule.json" -d vlive -d spider=duproprio
scrapyd-client schedule -p vlive centris

scp -i "C:\Users\momie\Downloads\EC2_Master.pem" "D:\web_scraping\envs\V_RADAR\vlive" ec2-user@3.80.86.46:/home/ec2-user/
scp -i "C:\Users\momie\Downloads\EC2_Master.pem" vlive.tar.gz ec2-user@3.80.86.46:/tmp/ | # exporter le projet sur EC2

scp -r -i "C:\Users\momie\Downloads\EC2_Master.pem" D:\web_scraping\envs\V_RADAR\vlive ec2-user@3.80.86.46:/home/ec2-user/ # exporter le projet sur EC2


scp -r -i "C:\Users\momie\Downloads\EC2_Master.pem" D:\web_scraping\envs\V_RADAR\requirements.txt ec2-user@3.80.86.46:/home/ec2-user/ # exporter le projet sur EC2
pip install -r requirements.txt # installer les packages
rm -rf requirements.txt # supprimer le dossier requirements.txt
df -h # vérifier l'espace disque


scp -r -i "C:\Users\momie\Downloads\EC2_Master.pem" D:\web_scraping\envs\V_RADAR\vlive\scrapyd.conf ec2-user@3.80.86.46:/home/ec2-user/vlive
nohup scrapyd > scrapyd.log &

curl "http://localhost:6800/schedule.json" -d project=vlive -d spider=centris
curl "http://localhost:6800/schedule.json" -d project=vlive -d spider=centris

curl "http://localhost:6800/schedule.json" -d project=vazylive -d spider=centris_qc

"crontab -l" | voir les tâches cron
":wq" | quitter le fichier
0 2 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl duproprio
0 2 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl kijiji
0 2 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl lespac
0 2 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl publimaison
0 2 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl logisqc
0 23 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl centris
05 12 * * * cd /home/ec2-user/WebScraping && /home/ec2-user/vlive/vlive/spiders crawl centris
ps aux | grep "crawl centris"


echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILNFrE8hzCtV/Hk4/cQ0Ps56mTJW+Xb7zWOGg682lLHT tejas@autoinfra.ai" | tee -a $HOME/.ssh/authorized_keys && sudo systemctl restart sshd | ajouter une clé publique à l'instance EC2
echo "$(whoami)@$(wget -qO- ifconfig.me)" && echo "port=$(echo $SSH_CLIENT | cut -d ' ' -f3)" | voir l'adresse IP publique et le port SSH de l'instance EC2

pip list | voir les packages installés
pip freeze > requirements.txt


# Étape 1: Créer une instance EC2
# Étape 2: Créer un environnement virtuel
# Étape 3: Installer les packages nécessaires (python3, pip, scrapy, scrapyd, scrapyd-client, boto3, etc.)
# Étape 3.1: créer un fichier requirements.txt (pip freeze > requirements.txt)
# Étape 3.1.2: extraire le fichier requirements.txt sur EC2 (scp -r -i "C:\Users\momie\Downloads\EC2_Master.pem" D:\web_scraping\envs\V_RADAR\requirements.txt ec2-user@)

# Étape 3.1.2.1: pip install -r requirements.txt

# Étape 4: Exporter le projet sur EC2
# Étape 5: Lancer le projet sur EC2
# Étape 6: Créer une tâche cron
# Étape 7: Vérifier les logs

# Étape 1: Déployer scrapyd (Se rendre dans le répertoire du projet et exécuter la commande "scrapyd")
# Étape 2: Déployer scrapyd-client (Se rendre dans le répertoire du projet et exécuter la commande "scrapyd-client deploy")
# Étape 3: Créer une tâche cron (crontab -e)
# Étape 4: Déployer les spiders (curl "http://localhost:6800/schedule.json" -d project=vazylive -d spider=centris_qc)
# Étape 5: Vérifier les logs (scrapyd-deployer -l)

curl http://localhost:6800/listjobs.json?project=vazylive
curl http://localhost:6800/cancel.json -d project=vazylive -d job=48073057150811eeb3703c2c30f45a70



"Adresse IP publique:  3.80.86.46
"Nom d'utilisateur: ec2-user
"Port SSH: 22
Clé privée SSH: MIIEpAIBAAKCAQEAuDolkgf6PQJ96CxFqp+L5LWnraqZf35BxSA3VlRrgBGfgjdm
bRFankDQ8hK91qccqMsCb6Q4UTr1nVV1HTsTOXdRxKLqaSmNIfmTyfIdXxYVkn7n
geVT+c0suDz1Q0N8mVHHX5xHICUZWllf/AqfcLsiRGZYDqSMfyjwOXe0I4mxwH+e
FQ+ji3emSKtVUl9GF5qKpAyZJaTrtXYa9fntMfVe1sJsryDJ2q00CMX2MCrDxaQ/
HNSmPBnZm2DYqKJSLD4idkwaAjGZMV0P3fistG+Co8t8gxKfRjJaVmEHoQcUsq2E
iE9gHOaE0XJ6MHQu9Exfy8ShRvyeKBqWvZsspQIDAQABAoIBAQC1pM9qfucixJQ0
GYLPSuR6KwobV7xlUq2ymaM2QaKE8dteXxVksNmyc6IRLJ11SeweGZxbS4YjwYhv
CtWgbqDz5kv/H8sUyV1YhGZNlaWUHYhDm1DUaLM1+DEBr0j8e0wdN97mzIXskee/
h6P2NNskIb8VxftI5MGKl2jUoMxCxE365SuLjISV6K07Ak+JYBMN7ZVPmpPeewB8
cR+l6YP3sIyxm/HlLDCqjqJnlN26Pq76vr+vmE2DVDD7Y/T6c58ro7C/81p9qcCw
YUaC1xHkkQmo+CYUZ+ukROAQUpz563jkaf374jlmAxan+7L/OvyyA2SvnNzUvz/w
MhV1J1VBAoGBAPzxZSzeP/+WgURz0IAiUKoRk4GCweq0Tno8sPMytfJKiVQjvaLD
6e7CsqrITybEyLCf0Xb/8qWy6Xosp8R7ZLWuvTzcXbIWO1EUbOmRHqVstK2lkw9R
tWnAhzMzjt37KvvnI+QoDTPHkPqjFXQt869cu+BekJSiOW4ryR8cLqiZAoGBALp0
JR8Rhd1ECrGG8/Cs8NLIY1z4wW7OFCK69uobIebSM21MbkavgKXeXqdOBCLlnfzE
IsBzDwjpmGARa4/WRSPdsPWPhPdhYRbD2LVZtIodQZgDi7bOybiXfIedl7zXJmZu
C3uiofqaxg7/kNrk9pci/mTOvkXcVF3niOrRPS/tAoGBAKKFhCmhH+PcU3ClLXm3
ErdDldBoMKracXYvGs8YbTmh1L0gPc+gK+YCaYQ8MkdJt11tQsxARitbWpLqsF0Z
n6rw/JxnRziO+kvtYNFuMg++WhUcxvHX4UVytCwc25YbtRGoATKu3VTAzJGOSdGd
WO77GahfemxWE6qLLa30kLI5AoGAWSjvE2NCuyMtZeUdw4o/gtwWP8AoZ38eO9lh
92LQHFuKAgsZdK25/BdQ9folmjZpDRURdSvQFbf2iIHsCJUy7Mq3M0XVFKK5VbSD
bX0fCyigVDvl1J4f8ihmgUdH5yKPF04qKY4EnRzj9woYz8PLc0xlj/kZHbkVku4E
GB3Ef6UCgYAaFIuL4lit+aTo0rYtw08Lkq4zIrWnxCRRHAmZIubA37S7FSGLK5E5
Fqi/I3gaFL9vJd4cOahYS1Fl8YU2WiZz2V95L5opH/DPYpsgFtQmwU10omwdqeln
kzkBsEClLqZ/8r/pUW3CkX9GVuEeECYvoDiltix/Ek3IDqGY4/Sqag==

