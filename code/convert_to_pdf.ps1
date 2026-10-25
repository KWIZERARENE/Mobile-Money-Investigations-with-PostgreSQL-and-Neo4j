$ErrorActionPreference = "Stop"

$docxPath = "C:\assignement\report\Assignment_II_Group_Report.docx"
$pdfPath = "C:\assignement\report\Assignment_II_Group_Report.pdf"

Write-Host "Starting Word Application for PDF conversion..."
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    Write-Host "Opening document: $docxPath"
    $doc = $word.Documents.Open($docxPath, [Type]::Missing, $true) # open read-only
    
    Write-Host "Exporting to PDF: $pdfPath"
    # wdExportFormatPDF = 17
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    
    Write-Host "PDF Export complete!"
    $doc.Close([ref]0) # wdDoNotSaveChanges
}
catch {
    Write-Error "Failed to convert document: $_"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

$pdfItem = Get-Item $pdfPath
Write-Host "Successfully generated PDF: $($pdfItem.FullName) ($($pdfItem.Length) bytes)"
