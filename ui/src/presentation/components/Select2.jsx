import React from 'react';
import Select from 'react-select';

export const Select2 = ({
    label,
    options,
    value,
    onChange,
    isMulti = false,
    placeholder = 'Select...',
    isSearchable = true,
    error,
    ...props
}) => {
    const customStyles = {
        control: (provided, state) => ({
            ...provided,
            backgroundColor: '#1A1A1A',
            borderColor: state.isFocused ? '#6366F1' : '#1E1E1E',
            borderRadius: '0.5rem',
            padding: '0.25rem',
            boxShadow: state.isFocused ? '0 0 0 2px rgba(99, 102, 241, 0.2)' : 'none',
            '&:hover': {
                borderColor: state.isFocused ? '#6366F1' : '#2A2A2A'
            }
        }),
        menu: (provided) => ({
            ...provided,
            backgroundColor: '#121212',
            border: '1px solid #1E1E1E',
            borderRadius: '0.5rem',
            overflow: 'hidden'
        }),
        option: (provided, state) => ({
            ...provided,
            backgroundColor: state.isSelected
                ? '#6366F1'
                : state.isFocused
                    ? '#1A1A1A'
                    : '#121212',
            color: '#E5E5E5',
            cursor: 'pointer',
            '&:active': {
                backgroundColor: '#6366F1'
            }
        }),
        multiValue: (provided) => ({
            ...provided,
            backgroundColor: '#6366F1',
            borderRadius: '0.375rem',
        }),
        multiValueLabel: (provided) => ({
            ...provided,
            color: '#ffffff',
            padding: '0.25rem 0.5rem'
        }),
        multiValueRemove: (provided) => ({
            ...provided,
            color: '#ffffff',
            ':hover': {
                backgroundColor: '#4F46E5',
                color: '#ffffff'
            }
        }),
        input: (provided) => ({
            ...provided,
            color: '#E5E5E5'
        }),
        placeholder: (provided) => ({
            ...provided,
            color: '#6B7280'
        }),
        singleValue: (provided) => ({
            ...provided,
            color: '#E5E5E5'
        }),
        dropdownIndicator: (provided) => ({
            ...provided,
            color: '#6B7280',
            '&:hover': {
                color: '#E5E5E5'
            }
        }),
        clearIndicator: (provided) => ({
            ...provided,
            color: '#6B7280',
            '&:hover': {
                color: '#E5E5E5'
            }
        })
    };

    return (
        <div className="flex flex-col gap-1.5">
            {label && (
                <label className="text-sm font-medium text-gray-300">
                    {label}
                </label>
            )}
            <Select
                options={options}
                value={value}
                onChange={onChange}
                isMulti={isMulti}
                placeholder={placeholder}
                isSearchable={isSearchable}
                styles={customStyles}
                theme={(theme) => ({
                    ...theme,
                    colors: {
                        ...theme.colors,
                        primary: '#6366F1',
                        primary25: '#1A1A1A',
                        primary50: '#2A2A2A',
                        neutral0: '#121212',
                        neutral5: '#1A1A1A',
                        neutral10: '#1E1E1E',
                        neutral20: '#2A2A2A',
                        neutral30: '#3A3A3A',
                        neutral40: '#6B7280',
                        neutral50: '#6B7280',
                        neutral60: '#9CA3AF',
                        neutral70: '#D1D5DB',
                        neutral80: '#E5E5E5',
                        neutral90: '#F3F4F6',
                    }
                })}
                {...props}
            />
            {error && (
                <span className="text-xs text-red-400">{error}</span>
            )}
        </div>
    );
};
