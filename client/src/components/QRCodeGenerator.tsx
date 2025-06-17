import React, { useState } from 'react';
import QRCode from 'react-qr-code';
import { Button, Box, Slider, Typography, Paper } from '@mui/material';
import { ErrorBoundary } from 'react-error-boundary';

interface QRCodeGeneratorProps {
  url?: string;
  initialSize?: number;
}

const QRCodeGenerator: React.FC<QRCodeGeneratorProps> = ({ 
  url = window.location.href,
  initialSize = 200 
}) => {
  const [size, setSize] = useState(initialSize);
  const [qrRef, setQrRef] = useState<HTMLDivElement | null>(null);

  const handleDownload = () => {
    if (qrRef) {
      const svg = qrRef.querySelector('svg');
      if (svg) {
        const svgData = new XMLSerializer().serializeToString(svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
          if (ctx) {
            canvas.width = size;
            canvas.height = size;
            ctx.drawImage(img, 0, 0);
            const pngFile = canvas.toDataURL('image/png');
            
            const downloadLink = document.createElement('a');
            downloadLink.download = 'qr-code.png';
            downloadLink.href = pngFile;
            downloadLink.click();
          }
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
      }
    }
  };

  const handleSizeChange = (_: Event, value: number | number[]) => {
    setSize(value as number);
  };

  return (
    <Box sx={{ p: 2, maxWidth: 400, mx: 'auto' }}>
      <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom>
          QR Code Generator
        </Typography>
        
        <Box ref={setQrRef} sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
          <QRCode
            value={url}
            size={size}
            style={{ height: 'auto', maxWidth: '100%', width: '100%' }}
            viewBox={`0 0 ${size} ${size}`}
          />
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography gutterBottom>Size: {size}px</Typography>
          <Slider
            value={size}
            onChange={handleSizeChange}
            min={100}
            max={400}
            step={10}
            aria-label="QR Code Size"
          />
        </Box>

        <Button
          variant="contained"
          color="primary"
          onClick={handleDownload}
          fullWidth
        >
          Download QR Code
        </Button>
      </Paper>
    </Box>
  );
};

// Error Fallback Component
const ErrorFallback: React.FC<{ error: Error }> = ({ error }) => (
  <Box sx={{ p: 2, textAlign: 'center', color: 'error.main' }}>
    <Typography variant="h6">Something went wrong:</Typography>
    <Typography>{error.message}</Typography>
  </Box>
);

// Wrapped Component with Error Boundary
const QRCodeGeneratorWithErrorBoundary: React.FC<QRCodeGeneratorProps> = (props) => (
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <QRCodeGenerator {...props} />
  </ErrorBoundary>
);

export default QRCodeGeneratorWithErrorBoundary; 