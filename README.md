# keepactive_msteams

To keep the MS Teams (PWA) window always active on Linux.

## How to use
1. Give the script execution permission
```
chmod +x keep_active.sh
```
2. Open MS Teams (PWA) and set your desired online status
3. To run the script
```
./keep_active.sh &
```
4. To gracefully terminate script execution
 ```
 touch /tmp/stop_keep_active
 ```
## Optional command
1. To view execution logs
 ```
 tail -f /tmp/keep_active.log
 ```
