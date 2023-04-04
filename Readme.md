# BME210 2023
## Competion Files
### Mechanical Files
- [Game Piece](https://cad.onshape.com/documents/893bf208592d3efc1aecf386/w/71abcb1ee77db1a483d59877/e/efb70fcf7bd54432a142c368?renderMode=0&uiState=642b7a062784d231f4efae18)
- [Game Piece Handler](https://cad.onshape.com/documents/21bc9d9502628244e6b1a21a/w/3563904f30ac23b3bb95a2f4/e/da1ce2869d822480df9112d5?renderMode=0&uiState=642b7ab6e60a373733bf017b)
- [Field](https://cad.onshape.com/documents/d0a2a9d3c5d141d21c35f5f2/w/92f3b9cb313965578f4ade22/e/ae98a8d43e3b5fd6aa1226c8?renderMode=0&uiState=642b7a5fd195c637d1b4b34a)
- [Camera Mount](https://cad.onshape.com/documents/228bddf0c8fe227d6238339f/w/07235dd6cc83dffb4aa64e34/e/c662a7628ecc89cd6f884a7e?renderMode=0&uiState=642b7af37612b95cb88c6ea0)
### Software
#### Camera
- PiCamera2 framework
- MAC/PC framework
- Vision Pipeline
- ZeroMQ publishing
#### Robotic Arm
- meArm, kinematics
- JoyStick
- Throw
- ZeroMQ Receiver 
- Defense - Attack

#### Running Python Program at Boot

``` 
cd /lib/systemd/system/
sudo nano my.service
```
should have following conent
```
[Unit]
Description=Hello World
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python /home/pi/myprogram.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```
Update the file, make it executable and run it
```
sudo chmod 644 /lib/systemd/system/my.service
chmod +x /home/pi/myprogram.py
sudo systemctl daemon-reload
sudo systemctl enable my.service
sudo systemctl start my.service
```

And check it its running
```
sudo systemctl status my.service
```
Stop if you want to modify it
```
sudo systemctl stop my.service
```
