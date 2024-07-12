/* eslint-disable react/prop-types */

import { MultiSelect as PrimeMultiSelect } from 'primereact/multiselect'

const MultiSelect = ({
	options,
	selectedValues,
	setSelectedValues,
	selectAllLabel = 'Select All',
	selectedItemsLabel = `${selectedValues.length} items selected`,
	maxSelectedLabels = 0,
	selectAll = true,
	label,
	// optionLabel = 'name',
	placeholder = 'Select...',
	className = 'bg-darkblueLight text-white text-xs m-0 w-full rounded-md',
}) => {
	return (
		<div>
			<PrimeMultiSelect
				selectAllLabel={selectAllLabel}
				selectedItemsLabel={selectedItemsLabel}
				maxSelectedLabels={maxSelectedLabels}
				selectAll={selectAll}
				value={selectedValues}
				onChange={(e) => setSelectedValues(e.value)}
				options={options}
				// optionLabel={optionLabel}
				placeholder={placeholder}
				className={className}
			/>
			<label htmlFor={label}>{label}</label>
		</div>
	)
}

export default MultiSelect
