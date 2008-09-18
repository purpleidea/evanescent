import servicemanager

servicemanager.SetEventSourceName('evanescent test')

servicemanager.LogInfoMsg('info msg')
servicemanager.LogWarningMsg('warning msg')
servicemanager.LogErrorMsg('error msg')