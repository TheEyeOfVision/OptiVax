// components/Header.js
import React from 'react';

const Header = ({ onFileUpload, uploadedFileName }) => {
  return (
    <header>
      <div className="upload-container">
        <button className="upload-btn">
          <input type="file" onChange={onFileUpload} />
          Upload CSV
        </button>
        {uploadedFileName && <span className="uploaded-file">{uploadedFileName}</span>}
      </div>
    </header>
  );
};

export default Header;
