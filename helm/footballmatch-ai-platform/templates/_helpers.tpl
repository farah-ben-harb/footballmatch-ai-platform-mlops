{{- define "footballmatch.name" -}}
footballmatch-ai-platform
{{- end -}}
{{- define "footballmatch.fullname" -}}
{{- .Release.Name }}-{{ include "footballmatch.name" . }}
{{- end -}}
