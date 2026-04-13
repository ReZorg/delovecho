# ALP XML Element Templates

## Root Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<AnyLogicWorkspace WorkspaceVersion="1.9" AnyLogicVersion="8.6.0" AlpVersion="8.5.7">
<Model>
  <Id>{model_id}</Id>
  <Name><![CDATA[{model_name}]]></Name>
  <Description><![CDATA[{description}]]></Description>
  <EngineVersion>6</EngineVersion>
  <JavaPackageName><![CDATA[{package_name}]]></JavaPackageName>
  <ModelTimeUnit><![CDATA[{time_unit}]]></ModelTimeUnit>
  <ActiveObjectClasses>...</ActiveObjectClasses>
  <Experiments>...</Experiments>
  <ModelResources>...</ModelResources>
  <RequiredLibraryReference>...</RequiredLibraryReference>
</Model>
</AnyLogicWorkspace>
```

## Variable Classes
- StockVariable: SD stock with InitialValue
- Flow: SD flow with Formula, SourceId/DestinationId
- AuxVariable: Dynamic variable with Formula
- PlainVariable: Simple variable with InitialValue
- Parameter: Model parameter with DefaultValue

## EmbeddedObject Classes (Process Modeling Library)
- Source, Sink, Queue, Delay, Service, Hold, ResourcePool, SelectOutput, Combine, Seize, Release, Batch, Unbatch

## StatechartElement Classes
- State (ParentState="ROOT_NODE"): with Width/Height/FillColor
- Transition (ParentState="ROOT_NODE"): with Source/Target IDs, Trigger type (condition/timeout/rate/message)
- EntryPoint: Initial state pointer
- Branch: Decision point

## Event TriggerTypes
- condition: fires when boolean condition becomes true
- timeout: fires after specified time
- rate: fires at specified rate
