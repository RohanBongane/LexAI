$docxPath = (Resolve-Path "Legal_AI_Seminar_Synopsis_Final.docx").Path
$pdfPath = [System.IO.Path]::ChangeExtension($docxPath, ".pdf")

Write-Host "Converting DOCX to PDF using Microsoft Word..."
Write-Host "Input:  $docxPath"
Write-Host "Output: $pdfPath"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = [Microsoft.Office.Interop.Word.WdAlertLevel]::wdAlertsNone

try {
    $doc = $word.Documents.Open($docxPath, $false, $true)
    # wdFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close([ref]$false)
    Write-Host "Conversion completed successfully!"
}
catch {
    Write-Error "Error during Word conversion: $_"
}
finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
}
