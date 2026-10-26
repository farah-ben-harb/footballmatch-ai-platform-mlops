{{- define "footballmatch-ai.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "footballmatch-ai.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "footballmatch-ai.labels" -}}
app.kubernetes.io/name: {{ include "footballmatch-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end }}

{{- define "footballmatch-ai.selectorLabels" -}}
app.kubernetes.io/name: {{ include "footballmatch-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
