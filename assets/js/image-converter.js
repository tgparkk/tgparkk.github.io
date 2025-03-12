document.addEventListener('DOMContentLoaded', function() {
    // DOM 요소 참조
    const imageInput = document.getElementById('image-input');
    const fileName = document.getElementById('file-name');
    const previewContainer = document.getElementById('preview-container');
    const previewImage = document.getElementById('preview-image');
    const originalFormat = document.getElementById('original-format');
    const imageSize = document.getElementById('image-size');
    const imageDimensions = document.getElementById('image-dimensions');
    const conversionOptions = document.getElementById('conversion-options');
    const formatButtons = document.querySelectorAll('.format-button');
    const qualitySlider = document.getElementById('quality-slider');
    const qualityValue = document.getElementById('quality-value');
    const resizeWidth = document.getElementById('resize-width');
    const resizeHeight = document.getElementById('resize-height');
    const maintainRatio = document.getElementById('maintain-ratio');
    const resultContainer = document.getElementById('result-container');
    const resultImage = document.getElementById('result-image');
    const resultFormat = document.getElementById('result-format');
    const resultSize = document.getElementById('result-size');
    const resultDimensions = document.getElementById('result-dimensions');
    const downloadButton = document.getElementById('download-button');
    
    // 전역 변수
    let originalFile = null;
    let originalImageObj = null;
    let originalImageWidth = 0;
    let originalImageHeight = 0;
    let aspectRatio = 0;
    let selectedFormat = 'jpeg';
    
    // 파일 입력 변경 핸들러
    imageInput.addEventListener('change', handleFileSelect);
    
    // 포맷 버튼 클릭 핸들러
    formatButtons.forEach(button => {
      button.addEventListener('click', function() {
        formatButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
        selectedFormat = this.getAttribute('data-format');
        convertImage();
      });
    });
    
    // 품질 슬라이더 변경 핸들러
    qualitySlider.addEventListener('input', function() {
      qualityValue.textContent = this.value + '%';
      convertImage();
    });
    
    // 해상도 유지 체크박스 핸들러
    maintainRatio.addEventListener('change', function() {
      if (this.checked && originalImageObj) {
        updateDimensionsWithRatio();
      }
    });
    
    // 너비 입력 핸들러
    resizeWidth.addEventListener('input', function() {
      if (maintainRatio.checked && originalImageObj) {
        const newWidth = parseInt(this.value) || 0;
        if (newWidth > 0) {
          resizeHeight.value = Math.round(newWidth / aspectRatio);
        } else {
          resizeHeight.value = '';
        }
      }
      convertImage();
    });
    
    // 높이 입력 핸들러
    resizeHeight.addEventListener('input', function() {
      if (maintainRatio.checked && originalImageObj) {
        const newHeight = parseInt(this.value) || 0;
        if (newHeight > 0) {
          resizeWidth.value = Math.round(newHeight * aspectRatio);
        } else {
          resizeWidth.value = '';
        }
      }
      convertImage();
    });
    
    // 다운로드 버튼 클릭 핸들러
    downloadButton.addEventListener('click', downloadConvertedImage);
    
    // 비율을 유지하며 높이/너비 업데이트
    function updateDimensionsWithRatio() {
      if (resizeWidth.value) {
        const newWidth = parseInt(resizeWidth.value);
        resizeHeight.value = Math.round(newWidth / aspectRatio);
      } else if (resizeHeight.value) {
        const newHeight = parseInt(resizeHeight.value);
        resizeWidth.value = Math.round(newHeight * aspectRatio);
      }
    }
    
    // 파일 선택 처리
    function handleFileSelect(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      originalFile = file;
      fileName.textContent = file.name;
      
      // 파일 형식 확인
      const fileExtension = file.name.split('.').pop().toLowerCase();
      originalFormat.textContent = file.type || `.${fileExtension} file`;
      
      // 파일 크기 표시
      imageSize.textContent = formatFileSize(file.size);
      
      // 이미지 프리뷰 표시
      const reader = new FileReader();
      reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        conversionOptions.style.display = 'block';
        
        // 이미지 크기 정보 가져오기
        const img = new Image();
        img.onload = function() {
          originalImageWidth = img.width;
          originalImageHeight = img.height;
          aspectRatio = originalImageWidth / originalImageHeight;
          originalImageObj = img;
          
          imageDimensions.textContent = `${originalImageWidth} x ${originalImageHeight} px`;
          
          // 초기 포맷 버튼 활성화
          formatButtons[0].click();
        };
        img.src = e.target.result;
      };
      reader.readAsDataURL(file);
    }
    
    // 이미지 변환 처리
    function convertImage() {
      if (!originalFile || !originalImageObj) return;
      
      const quality = parseInt(qualitySlider.value) / 100;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // 리사이징 적용
      let outputWidth = originalImageWidth;
      let outputHeight = originalImageHeight;
      
      if (resizeWidth.value && parseInt(resizeWidth.value) > 0) {
        outputWidth = parseInt(resizeWidth.value);
      }
      
      if (resizeHeight.value && parseInt(resizeHeight.value) > 0) {
        outputHeight = parseInt(resizeHeight.value);
      }
      
      canvas.width = outputWidth;
      canvas.height = outputHeight;
      
      // 캔버스에 이미지 그리기
      ctx.drawImage(originalImageObj, 0, 0, outputWidth, outputHeight);
      
      // 출력 형식 및 품질 설정
      let mimeType;
      let outputBlob;
      
      switch (selectedFormat) {
        case 'png':
          mimeType = 'image/png';
          outputBlob = canvas.toDataURL(mimeType);
          break;
        case 'webp':
          mimeType = 'image/webp';
          outputBlob = canvas.toDataURL(mimeType, quality);
          break;
        case 'bmp':
          mimeType = 'image/bmp';
          outputBlob = canvas.toDataURL(mimeType);
          break;
        case 'tiff':
          mimeType = 'image/tiff';
          // TIFF 형식은 브라우저에서 직접 지원이 제한적이므로 
          // PNG로 변환 후 사용자에게 TIFF로 다운로드하도록 처리
          outputBlob = canvas.toDataURL('image/png');
          break;
        case 'jpeg':
        default:
          mimeType = 'image/jpeg';
          outputBlob = canvas.toDataURL(mimeType, quality);
          break;
      }
      
      // 결과 표시
      resultImage.src = outputBlob;
      resultContainer.style.display = 'block';
      resultFormat.textContent = mimeType;
      resultDimensions.textContent = `${outputWidth} x ${outputHeight} px`;
      
      // 파일 크기 계산 (Data URL의 대략적인 크기)
      const base64Data = outputBlob.split(',')[1];
      const approximateSize = Math.round((base64Data.length * 3) / 4);
      resultSize.textContent = formatFileSize(approximateSize);
    }
    
    // 변환된 이미지 다운로드
    function downloadConvertedImage() {
      if (!resultImage.src || resultImage.src === '#') return;
      
      // 파일 이름 생성
      const originalName = originalFile.name.split('.')[0];
      let extension;
      
      switch (selectedFormat) {
        case 'png': extension = 'png'; break;
        case 'webp': extension = 'webp'; break;
        case 'bmp': extension = 'bmp'; break;
        case 'tiff': extension = 'tif'; break;
        case 'jpeg':
        default: extension = 'jpg'; break;
      }
      
      const fileName = `${originalName}-converted.${extension}`;
      
      // Data URL을 Blob으로 변환
      fetch(resultImage.src)
        .then(res => res.blob())
        .then(blob => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          URL.revokeObjectURL(url);
          a.remove();
        });
    }
    
    // 파일 크기 포맷팅 (바이트 -> KB, MB)
    function formatFileSize(bytes) {
      if (bytes < 1024) {
        return bytes + ' bytes';
      } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(2) + ' KB';
      } else {
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
      }
    }
    
    // 페이지 로드 시 JPEG 포맷 버튼 활성화
    window.addEventListener('load', function() {
      formatButtons[0].classList.add('active');
    });
  });