/* eslint-disable react/prop-types */

import { createContext, useState } from 'react'
import { architectureOptions, packageOptions } from '../data/optionsData'

const AnalysisContext = createContext()

export const AnalysisProvider = ({ children }) => {
	const [selectedFunctions, setSelectedFunctions] = useState([]) // default value is ['all']
	const [analysis, setAnalysis] = useState([])
	const [analysisDetail, setAnalysisDetail] = useState([])
	const [currentReportID, setCurrentReportID] = useState(null)
	const [rowsPerPage, setRowsPerPage] = useState(5)
	const [continuationToken, setContinuationToken] = useState('')

	const [startDate, setStartDate] = useState(null)
	const [endDate, setEndDate] = useState(null)


	const [summary, setSummary] = useState({})
	const [downloadURL, setDownloadURL] = useState('')
	const [status, setStatus] = useState('')

	const [initialRuntime, setInitialRuntime] = useState([])
	const [selectedRuntime, setSelectedRuntime] = useState([])

	const [initialPackageOptions, setInitialPackageOptions] =
		useState(packageOptions)
	const [selectedPackageOptions, setSelectedPackageOptions] = useState([])

	const [initialArchitectureOptions, setInitialArchitectureOptions] =
		useState(architectureOptions)
	const [selectedArchitectureOptions, setSelectedArchitectureOptions] = useState(
		[]
	)

	return (
		<AnalysisContext.Provider
			value={{
				selectedFunctions,
				setSelectedFunctions,
				currentReportID,
				setCurrentReportID,
				analysis,
				setAnalysis,
				analysisDetail,
				setAnalysisDetail,
				downloadURL,
				setDownloadURL,
				rowsPerPage,
				setRowsPerPage,
				continuationToken,
				setContinuationToken,
				summary,
				setSummary,
				status,
				setStatus,
				startDate,
				setStartDate,
				endDate,
				setEndDate,
				selectedRuntime,
				setSelectedRuntime,
				initialRuntime,
				setInitialRuntime,
				selectedPackageOptions,
				setSelectedPackageOptions,
				initialPackageOptions,
				setInitialPackageOptions,
				initialArchitectureOptions,
				setInitialArchitectureOptions,
				selectedArchitectureOptions,
				setSelectedArchitectureOptions,
			}}
		>
			{children}
		</AnalysisContext.Provider>
	)
}

export default AnalysisContext
