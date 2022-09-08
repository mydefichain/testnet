# DeFiChain Testnet Node
DeFiChain Testnet Masternode/Fullnode Installationscript incl. API

#### Requirements

- Debian 10/11 (KVM virtualization recommended)
- 2 Cores
- 4 GB Memory
- 60 GB SSD
- Registered Domain or Subdomain pointing to the IP address of your server

> :warning: Please note, the Script install Apache and configure it and change your Hostname and disable root-Access. Please use it only on a fresh installed system to avoid problems.  For test purposes only! At the moment it used a special defid for the Testnet-Environment. You can compare your Node with https://mydeficha.in/en/index.php?site=testnet to check correkt Chain and Blockheigt/Hash.

#### Installation

Login to your Server with SSH (Putty) as a root-User

```wget https://raw.githubusercontent.com/mydefichain/testnet/main/install_testnetnode.sh```  
```chmod 744 ./install_testnetnode.sh```  
```./install_testnetnode.sh USERNAME SERVERNAME DOMAIN VERSION```  

---
#### Example

```./install_testnetnode.sh defichain myMasternode freedomain.com 2.10.0```  

The Script creates a user named "defichain" and your Server is reachable at http://mymasternode.freedomain.com  

---

*You need a public DNS Record that points this Domain to your public IP-Address of your Server.*

After the Script is finished, restart your Server with ```shutdown -r now``` and Login with your newly created user and your new password.

Type ```su USERNAME /home/USERNAME/install_user.sh```

Example: ```su defichain /home/defichain/install_user.sh```

This second Script install the correct AIN-Version and use the latest Snapshot of the Testnet.

Finished. You can use your Testnetnode and can reach your API with http://yourdomain.com/api/



