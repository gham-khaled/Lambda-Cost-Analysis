/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */

import { useContext, useEffect, useState } from 'react'
import Header from '../partials/Header'
import Sidebar from '../partials/Sidebar'
import 'primereact/resources/themes/vela-green/theme.css'

import { Calendar } from 'primereact/calendar'
import { FloatLabel } from 'primereact/floatlabel'
import MultiSelect from '../components/MultiSelect'
import { RotatingLines } from 'react-loader-spinner'

import axios from 'axios'

import { architectureOptions, successMsgStyle } from '../data/optionsData'
import { InputText } from 'primereact/inputtext'
import AnalysisContext from '../contexts/AnalysisContext'
import { customToast } from '../utils/utils'
import { useNavigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'

const PROD_API_URL = window.PROD_URL_API

const Analysis = () => {
	const {
		startDate,
		setStartDate,
		endDate,
		setEndDate,
		setCurrentReportID,
		selectedRuntime,
		setSelectedRuntime,
		initialRuntime,
		setInitialRuntime,
		initialPackageOptions,
		setInitialPackageOptions,
		selectedPackageOptions,
		setSelectedPackageOptions,
		initialArchitectureOptions,
		setInitialArchitectureOptions,
		selectedArchitectureOptions,
		setSelectedArchitectureOptions,
		selectedFunctions,
		setSelectedFunctions,
	} = useContext(AnalysisContext)

	const columns = [
		{ Header: 'Function name', accessor: 'FunctionName' },
		{ Header: 'Runtime', accessor: 'Runtime' },
		{ Header: 'PackageType', accessor: 'PackageType' },
		{ Header: 'Architecture', accessor: 'Architectures' },
		{ Header: 'LastModified', accessor: 'LastModified' },
	]

	const [analysisID, setAnalysisID] = useState('')
	const { setAnalysisDetail } = useContext(AnalysisContext)

	const [loading, setLoading] = useState(false)
	const [isFetching, setIsFetching] = useState(false)
	const [maxAttemptsReached, setMaxAttemptsReached] = useState(false)
	const [lambdaFunctions, setLambdaFunctions] = useState([])

	const [isFiltered, setIsFiltered] = useState(false)
	const [showConfirmation, setShowConfirmation] = useState(false)
	const [confirmationData, setConfirmationData] = useState(null)

	const navigate = useNavigate()

	const handleFetchFunctions = async () => {
		setLoading(true)
		try {
			// API call to fetch lambda functions with parameters

			// const response = await axios.get(
			// 	'api/lambdaFunctions?selectedRuntime=$[selectedRuntime]',
			// 	{
			// 		params: new URLSearchParams({
			// 			selectedRuntime: isFiltered ? selectedRuntime : initialRuntime,
			// 			selectedPackageType: isFiltered
			// 				? selectedPackageOptions
			// 				: initialPackageOptions,
			// 			selectedArchitecture: isFiltered
			// 				? selectedArchitectureOptions
			// 				: initialArchitectureOptions,
			// 		}),
			// 	}
			// )

			// API call to fetch lambda functions without any parameters

			const response = await axios.get(`${PROD_API_URL}/lambda-functions`)
			const functions = response.data

			handleFilters(functions)
			setSelectedFunctions(functions)
			setLambdaFunctions(functions)

			// console.log('Lambda functions: ', functions)

			setLoading(false)
		} catch (error) {
			console.error('Error fetching lambda functions: ', error)
			setLoading(false)
		}
	}

	// Client side filter functions based on fetched data
	const handleFilters = (functions) => {
		if (!isFiltered) {
			// Only set the initial filters from the fetched data once
			const fetchedFilteredRuntime = [
				...new Set(functions.map((func) => func.Runtime)),
			]

			const fetchedFilteredPackageTypes = [
				...new Set(functions.map((func) => func.PackageType)),
			]

			const fetchedFilteredArchitectureOptions = [
				...new Set(functions.flatMap((func) => func.Architectures)),
			]

			setInitialRuntime(fetchedFilteredRuntime)
			setSelectedRuntime(fetchedFilteredRuntime)

			setInitialPackageOptions(fetchedFilteredPackageTypes)
			setSelectedPackageOptions(fetchedFilteredPackageTypes)

			setInitialArchitectureOptions(fetchedFilteredArchitectureOptions)
			setSelectedArchitectureOptions(fetchedFilteredArchitectureOptions)

			setIsFiltered(true) // Set the flag to true after the first filtering
		}
	}

	useEffect(() => {
		// Fetch lambda functions on component mount
		handleFetchFunctions()
	}, [])

	const errorMsgStyle = {
		fontSize: '12px',
		border: '0.4px solid #787474',
		borderRadius: '5px',
		background: '#253645',
		color: '#fff',
	}

	const handleShowConfirmation = () => {
		// Validation
		if (!startDate || !endDate) {
			customToast(
				'Please select both start and end dates',
				'❌',
				errorMsgStyle
			)
			return
		}

		if (selectedFunctions.length === 0) {
			customToast(
				'Please select at least one Lambda function',
				'❌',
				errorMsgStyle
			)
			return
		}

		const unixStartDate = new Date(startDate.setHours(0, 0, 0, 0)).toISOString()
		const unixEndDate = new Date(endDate.setHours(23, 59, 59, 999)).toISOString()
		const reportID = analysisID || Math.floor(Date.now() / 1000)

		setConfirmationData({
			reportID,
			startDate: unixStartDate,
			endDate: unixEndDate,
			selectedFunctionsCount: selectedFunctions.length,
		})
		setShowConfirmation(true)
	}

	const handleLaunchAnalysis = async () => {
		setShowConfirmation(false)

		const { reportID, startDate: unixStartDate, endDate: unixEndDate } = confirmationData

		localStorage.setItem('reportID', reportID.toString())
		setMaxAttemptsReached(false)
		setCurrentReportID(reportID)

		const payload = {
			lambda_functions_name: selectedFunctions.map(
				(lambdaFunction) => lambdaFunction['FunctionName']
			),
			report_id: reportID,
			start_date: unixStartDate,
			end_date: unixEndDate,
		}
		setIsFetching(true)

		try {
			const response = await axios.post(`${PROD_API_URL}/startExecution`, payload)
			customToast('Analysis launched successfully', '✅', successMsgStyle)

			// Wait for a few seconds with spinner before redirecting
			await delay(3000)

			// Navigate immediately to the report details page
			navigate(`/report/reportID=${reportID}`)
		} catch (error) {
			console.error('Error launching analysis: ', error)
			customToast('Failed to launch analysis', '❌', errorMsgStyle)
			setIsFetching(false)
		}
	}

	const getAnalysisDetail = async (reportID) => {
		try {
			const response = await fetchDataWithRetry(reportID)
			setAnalysisDetail(response.data)
			navigate(`/report/reportID=${reportID}`) // Navigate on success
		} catch (error) {
			console.error('Error fetching report details: ', error)
			// Display error message here
		} finally {
			// setLoading(false)
			setIsFetching(false)
		}
	}

	// Function to delay execution
	const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

	const fetchDataWithRetry = async (reportID, maxAttempts = 10) => {
		let attempts = 0

		while (attempts < maxAttempts) {
			// Retry fetching data 5 times b/c the API may not return the data immediately
			try {
				const response = await axios.get(
					`${PROD_API_URL}/report?reportID=${reportID}`
				)
				// console.log(`Report Detail Response: ${response}`)
				console.log(response)
				if (response.status === 200) {
					return response // Return response if successful
				}
				attempts++
				await delay(3000)
			} catch (error) {
				if (attempts === maxAttempts - 1) {
					customToast('Maximum attempts reached', '❌', errorMsgStyle)
					setMaxAttemptsReached(true)

					// console.error('Max attempts reached')
					throw error // Throw error on the last attempt
				}
				attempts++
				await delay(3000)
			}
		}
		throw new Error('Max attempts reached')
	}

	return (
		<div className='flex'>
			<Toaster />
			<Sidebar />
			<div className='bg-darkblue w-full h-screen overflow-y-scroll p-10 pt-0 space-y-6 '>
				<Header title='Analysis | New'></Header>
				<div className='col-span-12 lg:col-span-12 space-y-4 pt-8'>
					{lambdaFunctions.length !== 0 && (
						<>
							<div className='grid grid-cols-2 md:grid-cols-6  gap-x-6 gap-y-10 text-xs'>
								<FloatLabel>
									<MultiSelect
										options={initialRuntime}
										selectedValues={selectedRuntime}
										setSelectedValues={setSelectedRuntime}
										placeholder='Runtime'
										maxSelectedLabels={1}
										selectedItemsLabel={selectedRuntime[0] + ' ...'}
									/>
									<label htmlFor='runtime'>Runtime</label>
								</FloatLabel>

								<FloatLabel>
									<MultiSelect
										options={initialPackageOptions}
										selectedValues={selectedPackageOptions}
										setSelectedValues={setSelectedPackageOptions}
										placeholder='Package'
										maxSelectedLabels={1}
										selectedItemsLabel={selectedPackageOptions[0] + ' ...'}
									/>
									<label htmlFor='package_option'>Package</label>
								</FloatLabel>
								<FloatLabel>
									<MultiSelect
										options={initialArchitectureOptions}
										selectedValues={selectedArchitectureOptions}
										setSelectedValues={setSelectedArchitectureOptions}
										placeholder='Architecture'
										maxSelectedLabels={1}
										selectedItemsLabel={architectureOptions[0] + ' ...'}
									/>
									<label htmlFor='architecture_option'>Architecture</label>
								</FloatLabel>

								{/* Fetch Lambda function */}
								{/* <button
							className={`${!loading || (!loading && isFetching) ? 'bg-[#00A9817D] opacity-90 ' : 'bg-gray-500'} text-white text-xs p-2 rounded-md text-wrap`}
							onClick={handleFetchFunctions}
							disabled={loading || isFetching}
						>
							{loading ? 'Fetching Fns...' : 'Fetch Lambda Fns'}
						</button> */}
							</div>

							<div className='col-span-12 lg:col-span-12 space-y-4 pt-8'>
								<div className='grid grid-cols-2 md:grid-cols-6 text-[10px]  gap-x-6 gap-y-10'>
									<FloatLabel>
										<InputText
											id='analysis_id'
											value={analysisID}
											onChange={(e) => setAnalysisID(e.target.value)}
											className='bg-darkblueLight border-none text-white text-xs  py-2 px-6  rounded-md w-full'
										/>
										<label htmlFor='analysis_id'>Analysis ID (Optional)</label>
									</FloatLabel>
									<FloatLabel>
										<Calendar
											value={startDate}
											onChange={(e) => setStartDate(e.value)}
											showIcon
											showButtonBar
											className='bg-darkblueLight border-none text-white text-xs   rounded-md w-full'
											inputClassName='bg-darkblueLight text-white text-xs border-none px-2 py-2 rounded-md  '
										/>
										<label htmlFor='start_date'>Start Date</label>
									</FloatLabel>
									<FloatLabel>
										<Calendar
											value={endDate}
											onChange={(e) => {
												if (e.value > startDate) {
													setEndDate(e.value)
												}
											}}
											showIcon
											showButtonBar
											className='bg-darkblueLight border-none text-white text-xs   rounded-md w-full'
											inputClassName='bg-darkblueLight text-white text-xs border-none px-2 py-2  rounded-md'
										/>
										<label htmlFor='end_date'>End Date</label>
									</FloatLabel>

									<button
										className={`${!isFetching && startDate && endDate && selectedFunctions.length > 0 ? 'bg-lambdaPrimary hover:bg-green-600' : 'bg-gray-500 cursor-not-allowed'} text-white text-xs py-1 rounded-md transition-colors`}
										onClick={handleShowConfirmation}
										disabled={isFetching || !startDate || !endDate || selectedFunctions.length === 0}
									>
										{isFetching ? 'Launching Analysis...' : 'New Analysis'}
									</button>
								</div>
								{!startDate || !endDate ? (
									<div className='text-xs text-red-400 pt-4'>
										⚠️ Please select both start and end dates to launch the analysis
									</div>
								) : selectedFunctions.length === 0 ? (
									<div className='text-xs text-red-400 pt-4'>
										⚠️ Please select at least one Lambda function
									</div>
								) : null}
								{isFetching && (
									<div className='flex items-center gap-3 text-sm text-yellow-500 pt-4'>
										<RotatingLines
											visible={true}
											height='20'
											width='20'
											color='#eab308'
											strokeWidth='5'
											animationDuration='0.75'
											ariaLabel='rotating-lines-loading'
										/>
										<span>Launching analysis... You will be redirected shortly.</span>
									</div>
								)}
								{maxAttemptsReached && (
									<div className='text-xs text-red-600 pt-4'>
										Oops! Maximum attempts reached. Please try again later.
									</div>
								)}
							</div>
						</>
					)}
					<div className='pt-8'>
						<DynamicTable
							columns={columns}
							data={lambdaFunctions}
							loading={loading}
						/>
					</div>
				</div>

				{/* Confirmation Modal */}
				{showConfirmation && confirmationData && (
					<div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
						<div className='bg-darkblueMedium border border-darkblueLight rounded-lg p-8 max-w-md w-full mx-4'>
							<h2 className='text-xl font-semibold text-lambdaPrimary mb-4'>
								Confirm Analysis Launch
							</h2>
							<div className='space-y-3 text-sm text-white/80'>
								<div className='flex justify-between'>
									<span className='text-gray-400'>Analysis ID:</span>
									<span className='font-medium text-white'>{confirmationData.reportID}</span>
								</div>
								<div className='flex justify-between'>
									<span className='text-gray-400'>Start Date:</span>
									<span className='font-medium text-white'>
										{new Date(confirmationData.startDate).toLocaleDateString()}
									</span>
								</div>
								<div className='flex justify-between'>
									<span className='text-gray-400'>End Date:</span>
									<span className='font-medium text-white'>
										{new Date(confirmationData.endDate).toLocaleDateString()}
									</span>
								</div>
								<div className='flex justify-between'>
									<span className='text-gray-400'>Lambda Functions:</span>
									<span className='font-medium text-white'>
										{confirmationData.selectedFunctionsCount} selected
									</span>
								</div>
							</div>
							<div className='flex gap-4 mt-6'>
								<button
									onClick={() => setShowConfirmation(false)}
									className='flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-md text-sm transition-colors'
								>
									Cancel
								</button>
								<button
									onClick={handleLaunchAnalysis}
									className='flex-1 bg-lambdaPrimary hover:bg-green-600 text-white py-2 px-4 rounded-md text-sm transition-colors'
								>
									Launch Analysis
								</button>
							</div>
						</div>
					</div>
				)}
			</div>
		</div>
	)
}

const DynamicTable = ({ columns, data, loading = false }) => {
	const {
		setSelectedFunctions,
		selectedRuntime,
		selectedArchitectureOptions,
		selectedPackageOptions,
	} = useContext(AnalysisContext)
	const [checkedItems, setCheckedItems] = useState({})

	// Apply filters to get the filtered data
	const filteredData = data.filter(
		(row) =>
			selectedRuntime.includes(row.Runtime) &&
			selectedPackageOptions.includes(row.PackageType) &&
			selectedArchitectureOptions.some(
				(architecture) => row.Architectures.includes(architecture)
			)
	)

	useEffect(() => {
		// Initialize or reset checkedItems state when filtered data changes
		const newCheckedItems = {}
		filteredData.forEach((item, index) => {
			newCheckedItems[index] = true // Initially, all items are checked
		})
		setCheckedItems(newCheckedItems)
		// Update selected functions with filtered data
		setSelectedFunctions(filteredData)
	}, [data, selectedRuntime, selectedPackageOptions, selectedArchitectureOptions])

	const handleSelectAll = (e) => {
		const newCheckedItems = {}
		filteredData.forEach((item, index) => {
			newCheckedItems[index] = e.target.checked
		})
		setCheckedItems(newCheckedItems)
		const selected = e.target.checked ? filteredData : []
		setSelectedFunctions(selected)
	}

	const handleSelectItem = (index, isChecked) => {
		const newCheckedItems = { ...checkedItems, [index]: isChecked }
		setCheckedItems(newCheckedItems)
		const selected = Object.keys(newCheckedItems)
			.filter((key) => newCheckedItems[key])
			.map((key) => filteredData[key])
			.filter(Boolean)
		setSelectedFunctions(selected)
	}

	const allChecked = filteredData.length > 0 && Object.values(checkedItems).every(Boolean)

	return (
		<>
			{data.length !== 0 ? (
				<div className='relative overflow-x-auto shadow-md sm:rounded-md'>
					<table className='w-full text-sm text-left rtl:text-right text-white border border-darkblueLight rounded-md'>
						<thead className='text-xs uppercase text-white bg-darkblueLight'>
							<tr>
								<th scope='col' className='px-6 py-3'>
									<input
										type='checkbox'
										checked={allChecked}
										onChange={handleSelectAll}
									/>
								</th>
								{columns.map((column) => (
									<th key={column.accessor} scope='col' className='px-6 py-3'>
										{column.Header}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{filteredData.map((row, index) => {
								return (
									<tr
										key={index}
										className={`${index % 2 === 0 ? 'bg-darkblueMedium' : 'bg-transparent'} cursor-pointer text-xs hover:bg-green-900/40`}
									>
										<td className='px-6 py-3'>
											<input
												type='checkbox'
												checked={checkedItems[index] || false}
												onChange={(e) => handleSelectItem(index, e.target.checked)}
											/>
										</td>
										{columns.map((column) => (
											<td key={column.accessor} className='px-6 py-3'>
												{column.Cell
													? column.Cell(row[column.accessor])
													: row[column.accessor]}
											</td>
										))}
									</tr>
								)
							})}
						</tbody>
					</table>
				</div>
			) : (
				<div className='text-gray-400 text-center flex justify-center items-center h-28 text-md mt-10'>
					{loading ? (
						<RotatingLines
							visible={true}
							height='40'
							width='40'
							color='darkblueLight'
							strokeWidth='5'
							animationDuration='1'
							ariaLabel='rotating-lines-loading'
							wrapperStyle={{}}
							wrapperClass=''
						/>
					) : (
						<>Data is not available</>
					)}
				</div>
			)}
		</>
	)
}

export default Analysis
