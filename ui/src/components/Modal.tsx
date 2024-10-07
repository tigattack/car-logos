import React, { useState } from "react";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  title: string;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, imageUrl, title }) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-opacity-10 flex items-center justify-center drop-shadow-2xl scale-150"
      onClick={onClose}
    >
      <div
        className="bg-white p-4 rounded shadow-lg relative"
        onClick={(e) => e.stopPropagation()}
      >
        {title ? (
          <h2 className="text-md text-gray-900 text-center">{title}</h2>
        ) : null}
        <button
          className="absolute top-2 right-2 text-gray-500 hover:text-gray-700"
          onClick={onClose}
        >
          &times;
        </button>
        <img
          src={imageUrl}
          alt="Modal Content"
          className="max-w-full h-auto rounded"
        />
      </div>
    </div>
  );
};

export default Modal;
