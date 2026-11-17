# Device signal model

The fields `device_agent/signals.py` generates, and what each is modeled on.
None of this is live device data -- it's a synthetic stand-in, generated
from a small set of staged scenarios, the same spirit as `voice-ai-agent`'s
`network_signals.py`.

| Field | Meaning | Modeled on |
|---|---|---|
| `device_id` | Synthetic handset identifier | -- |
| `timestamp` | When the reading was taken | -- |
| `serving_cell_id` | The cell the device is currently camped on | 3GPP UE Information Report (serving cell ID) |
| `rsrp_dbm` | Reference Signal Received Power | 3GPP RRC measurement report (RSRP) |
| `rsrq_db` | Reference Signal Received Quality | 3GPP RRC measurement report (RSRQ) |
| `recent_handover_attempts` | Handover attempts in the last window | 3GPP Minimization of Drive Tests (MDT) mobility logging |
| `recent_handover_failures` | Handover failures in the same window | 3GPP MDT mobility logging |
| `recent_call_drops` | Dropped-call events in the same window | 3GPP MDT radio link failure reports |
| `recent_retransmissions` | Retransmission count, a proxy for radio-link quality | 3GPP MDT / UE-side radio measurement logging |

## Why 3GPP and not TM Forum

TM Forum has no specification covering UE-side log or radio-diagnostic
content. `TMF908` (IoT Agent and Device Component Suite) is the closest
named candidate, but it's an IoT device-*management* spec (provisioning,
configuration, lifecycle) -- the wrong shape for "what a handset's radio
layer observed." 3GPP already defines UE-side mobility and radio-quality
reporting for exactly this purpose (MDT, UE Information Report, RRC
measurement reports), so the synthetic schema borrows field *concepts* from
those rather than TM Forum.

This is deliberately a simplified, illustrative schema -- it does not
reproduce the literal information-element encoding of the 3GPP
specifications, only the concepts they report on.
