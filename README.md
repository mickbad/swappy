# Swappy

Fast tools for checking swap memory and remove it in gnu/linux system

**Installation**

```bash
$ pip install swappy
```



**Usage for programming**

```python
# create automatic procedure
from swappy.swappy import swapcheck_main
config_pathname = "/path/to/config.yml"
swapcheck_main(config_pathname,
               simulation=False,
               display_stdout=True)

# personnal usage
from swappy.swappy import SwapInfo
swap = SwapInfo()
print(swap.swap_memory().percent) # percentage of swap
print(swap.swap_total)            # total swap taken by system
print(swap.count())               # total process found
print(swap.swap_info_text("pid")) # display text/plain output ordering by pid
print(swap.can_reset())           # can we reset swap with left memories?
```

**Usage for scripting**

```bash
$ swappy-check --help
Python script to check linux swap pressure
By Mickael Badet (prog at mickbad dot com)
https://github.com/mickbad/swappy

Usage: swappy-check [options] /path/to/config.yml

Options:
  -h, --help  show this help message and exit
  --info      show in stdout swap files if alert [default=False]
  --simulate  simulate resetting swap [default=False]
  
$ sudo swappy-check /path/to/swappy.yml
Swap Checker v1.0.0
swap pressure: 0.00%
```





**Configuration**

```yaml
# -------------------------------------------------------
# - YaML configuration for swappy checker
# -------------------------------------------------------

# configuration for swap alerting
swap:
  # percent alerting (float) **default = 50.0**
  alert-limit: 20.0

  # ordering for array in template (name, pid or swap)
  order-by: swap

  # reset swap if alert
  reset-swap: True

  # post process after alert
  post-process-alert:
    enable: True
    commands:
      # command list to after resetting
      - apt update
      - ls -la /tmp

  # send email to adminsys
  email:
    enable: True
    from: Alert Swap <my@email.com>
    subject: Alert swap on this server for {dd}/{mm}/{yyyy} - {H}:{M}:{S}
    to: my@email.com, my_another@email.com
    template: |
      <b>Alert swap detected:</b></br />
      ➡️ <u>percent info</u>: {swap_percent} %<br />
      ➡️ <u>list of pressure</u>:<br />
      {swap_list}<br />
      <br />
      AdminSys<br />

# SMTP Configuraiton
smtp:
  host: localhost
  port: 25
  tls: False
  login:
  password:
```
