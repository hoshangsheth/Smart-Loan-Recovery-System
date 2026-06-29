import { useState } from 'react';
import { FileDown, Loader2 } from 'lucide-react';
import Button from './Button';
import { downloadReport } from '../services/api';

export default function PdfDownloadButton({ result, input }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);

  async function handleDownload() {
    setIsDownloading(true);
    setDownloadError(null);
    try {
      const blob = await downloadReport({
        borrower_id: result.borrower_id,
        first_name: input.first_name,
        last_name: input.last_name,
        gender: input.gender,
        age: input.age,
        loan_type: input.loan_type,
        custom_scheme: input.interest_rate != null,
        monthly_income: input.monthly_income,
        loan_amount: input.loan_amount,
        outstanding_loan: input.outstanding_loan,
        loan_tenure: result.calculated.loan_tenure_used,
        interest_rate: result.calculated.interest_rate_used,
        collateral_value: input.collateral_value,
        missed_payments: input.missed_payments,
        days_past_due: result.calculated.days_past_due,
        collection_attempts: result.calculated.collection_attempts,
        monthly_emi: result.calculated.monthly_emi,
        emi_to_income: result.calculated.emi_to_income_ratio,
        collateral_coverage: result.calculated.collateral_coverage,
        default_severity: result.calculated.default_severity,
        risk_score: result.risk_score,
        risk_category: result.risk_category,
        strategy: result.strategy,
        segment_name: result.segment.segment_name,
        segment_description: result.segment.description,
      });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `borrower_report_${result.borrower_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setDownloadError(err.message || 'Could not generate the report. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <div>
      <Button variant="primary" onClick={handleDownload} disabled={isDownloading}>
        {isDownloading ? (
          <>
            <Loader2 size={16} className="animate-spin" /> Generating PDF…
          </>
        ) : (
          <>
            <FileDown size={16} /> Download Borrower PDF Report
          </>
        )}
      </Button>
      {downloadError && <p className="text-xs text-risk-high mt-2">{downloadError}</p>}
    </div>
  );
}
