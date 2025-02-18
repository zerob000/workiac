# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy
"""

import os

snames = ['AA', 'AAH', 'AAPRFE', 'ACA', 'ACM', 'AEROGEAR', 'AESH', 'AF', 'AG',
          'AGENT', 'AMQDOC', 'ANA', 'API', 'APIMAN', 'APPAI', 'APPSVC', 'ARQ', 
           'AUTH', 'BUILD', 'BXMSDOC', 'BYTEMAN', 'CCO', 'CDI', 'CDITCK', 'CEQ', 
          'CFE', 'CGW', 'CHE', 'CLAIRDEV', 'CLID', 'CLOUD', 'CM', 'CMCS', 'CMLK', 'CMP', 
          'CMTOOL', 'CNRDOC', 'CNV', 'COCKPIT', 'COMPOSER', 'CONSOLE', 'COO', 'CORS', 
          'COST', 'COS', 'CPE', 'CRW', 'CSB', 'CS', 'DBAAS', 'DBZ', 'DESIGN', 'DIRSRV', 
          'DMR', 'DROOLS', 'EAPDOC', 'EJBCLIENT', 'EJBTHREE', 'ELYEE', 'ELYWEB', 'ELY', 
          'ENTESB', 'ENTMQBR', 'ENTMQCL', 'ENTMQIC', 'ENTMQMAAS', 'ENTMQST', 'ENTMQ', 
          'ENTSBT', 'ENTVTX', 'ETCD', 'FAI', 'FDP', 'FLPATH', 'FORGE', 'FUSEDOC', 
          'FUSETOOLS', 'GITOPS', 'GRPA', 'HAL', 'HAWKULAR', 'HAWNG', 'HCCDDF', 'HCIDOCS', 
          'HELM', 'HIVE', 'HMS', 'HOSTEDCP', 'HRCPP', 'INSTALLER', 'IR', 'ISPN', 
          'JANDEX', 'JBAS', 'JBCS', 'JBDS', 'JBEAP', 'JBEE', 'JBERET','JBIDE', 
          'JBJCA', 'JBLOGGING', 'JBMAR', 'JBMETA', 'JBNAME', 'JBPAPP',
          'JBPM', 'JBTM', 'JBVFS', 'JBWS', 'JDF', 'JDG', 'JGRP', 'JKNS', 'JWS', 
          'KATA', 'KFLUXUI', 'KIECLOUD', 'KOGITO', 'LOGMGR', 'LOG', 'MAISTRA', 
          'MCO', 'MDC', 'MGDAPI', 'MGDOBR', 'MGDSR', 'MGDSTRM', 'MGDX', 'MIG', 
          'MODCLUSTER', 'MODE', 'MODULES', 'MON', 'MR', 'MSC', 'MTA', 'MTV', 
          'MULTIARCH', 'NE', 'NETOBSERV', 'NEXUS', 'NHE', 'NP', 'OADP', 'OBSDA', 
          'OBSDOCS', 'OCMUI', 'OCPBUGS', 'OCPBUILD', 'OCPCLOUD', 'OCPNODE', 'OCPPLAN', 
          'OCPSTRAT', 'ODC', 'ODH', 'OKD', 'OPCT', 'OPECO', 'OPENJDK', 'OPNET', 
          'OPRUN', 'ORG', 'OSASINFRA', 'OSJC', 'OSPK8', 'OSPRH', 'OSSM', 'OTA', 
          'OU', 'PD', 'PLANNER', 'PLINK', 'PODAUTO', 'PROJQUAY', 'PSAP', 'PTL', 
          'QDOCS', 'QUARKUS', 'RAT', 'RDO', 'REMJMX', 'RESTEASY', 'RFE', 'RHBK', 
          'RHBOP', 'RHBPMS', 'RHCLOUD', 'RHDEVDOCS', 'RHDM', 'RHELC', 'RHELDOCS', 
          'RHEL', 'RHIDP', 'RHINENG', 'RHODS', 'RHPAM', 'RHSSO', 'RUN', 'SAT', 
          'SBXBUG', 'SB', 'SDN', 'SDSTRAT', 'SECDATA', 'SECURITY', 'SHRINKRES', 
          'SHRINKWRAP', 'SKUPPER', 'SO', 'SPLAT', 'SRVKP', 'SRVLOGIC', 'SSLNTV', 
          'STOR', 'SWATCH', 'SWSQE', 'TACKLE', 'TEIIDDES', 'TEIID', 'TEST', 
          'THREESCALE', 'TRACING', 'TRT', 'UNDERTOW', 'USHIFT', 'VIRTSTRAT',
          'WEJBHTTP', 'WELD', 'WFARQ', 'WFCC', 'WFCOM', 'WFCORE', 'WFDISC', 'WFLY',
          'WFMP', 'WFNC', 'WFSSL', 'WFTC', 'WFWIP', 'WINC', 'AS7', 'REM3', 
          'WINDUPRULE', 'WINDUP', 'WRKLDS', 'WTO', 'XNIO', 'WAGB']
for sname in snames:
    os.system("python 1_Analyst.py RedHat.yaml "+sname)
    os.system("python 2_Scheduler.py RedHat.yaml "+sname)
    os.system("python 3_Strategist.py RedHat.yaml "+sname)
