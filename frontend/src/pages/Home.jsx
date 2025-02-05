/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */

import React, { useContext, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import AnalysisContext from '../contexts/AnalysisContext'

import Sidebar from '../partials/Sidebar'
import Header from '../partials/Header'
import { summaryColumns } from '../data/optionsData'
import { ThreeDots } from 'react-loader-spinner'

const PROD_API_URL = process.env.PROD_API_URL

const Home = () => {
	const [data, setData] = useState([])
	const [loading, setLoading] = useState(true)

	const { rowsPerPage, continuationToken, setContinuationToken } =
		useContext(AnalysisContext)

	useEffect(() => {
		fetchData()
	}, [rowsPerPage])

	const fetchData = () => {
		// console.log('Running FetchData')
		setLoading(true)
		setContinuationToken(null) // Reset the continuation token to avoid multiple requests
		axios
			.get(`${PROD_API_URL}/reportSummaries`, {
				params: {
					rowsPerPage: rowsPerPage,
					// continuationToken: token, // Use the provided token or the existing continuation token for subsequent requests
				},
			})
			.then((response) => {
				// console.log(response)
				if (response.data.message && response.data.message === 'No files found.') {
					setData([])
				} else {
					const { jsonContents, continuationToken: newContinuationToken } =
						response.data

					setData(jsonContents) // Append new data to existing data
					setContinuationToken(newContinuationToken) // Update the continuation token
				}

				// console.log('Data: ', response.data)
				setLoading(false)
			})
			.catch((error) => {
				console.error('Error fetching data: ', error)
				setLoading(false)
			})
	}

	return (
		<div className='flex'>
			<Sidebar />
			<div className='bg-darkblue w-full h-screen overflow-y-scroll p-10 pt-0 space-y-6 '>
				<Header title='Analysis | Home'></Header>
				<div className='pt-8'>
					<DynamicTable
						columns={summaryColumns}
						data={data}
						loading={loading}
						fetchData={fetchData}
						continuationToken={continuationToken}
					/>
				</div>
			</div>
		</div>
	)
}

const DynamicTable = ({
	columns = [],
	data,
	loading = false,
	fetchData,
	continuationToken,
}) => {
	const { rowsPerPage, setRowsPerPage } = useContext(AnalysisContext)

	const [currentPage, setCurrentPage] = useState(1)
	const [itemsPerPage, setItemsPerPage] = useState(rowsPerPage)
	const [sortConfig, setSortConfig] = useState({
		key: null,
		direction: 'ascending',
	})

	const sortedData = React.useMemo(() => {
		let sortableItems = [...data]
		if (sortConfig !== null) {
			sortableItems.sort((a, b) => {
				if (a[sortConfig.key] < b[sortConfig.key]) {
					return sortConfig.direction === 'ascending' ? -1 : 1
				}
				if (a[sortConfig.key] > b[sortConfig.key]) {
					return sortConfig.direction === 'ascending' ? 1 : -1
				}
				return 0
			})
		}
		return sortableItems
	}, [data, sortConfig])

	const requestSort = (key) => {
		let direction = 'ascending'
		if (sortConfig.key === key && sortConfig.direction === 'ascending') {
			direction = 'descending'
		}
		setSortConfig({ key, direction })
	}

	const indexOfLastItem = currentPage * itemsPerPage
	const indexOfFirstItem = indexOfLastItem - itemsPerPage
	const currentData = sortedData.slice(indexOfFirstItem, indexOfLastItem)

	const maxPages = Math.ceil(data.length / itemsPerPage)

	const handlePrevious = () =>
		setCurrentPage((current) => Math.max(current - 1, 1))
	const handleNext = () => {
		if (currentPage === maxPages) {
			// fetchData() // Fetch more data using the continuation token
			setCurrentPage((current) => Math.min(current + 1))
		} else {
			setCurrentPage((current) => Math.min(current + 1, maxPages))
		}
	}

	// useEffect(() => {
	// 	fetchData() // Call fetchData whenever rowsPerPage changes
	// }, [rowsPerPage]) // Add rowsPerPage as a dependency

	const handleItemsPerPageChange = (event) => {
		setRowsPerPage(Number(event.target.value))
		setItemsPerPage(Number(event.target.value))
		// fetchData() // Fetch data with the new items per page

		// setCurrentPage((current) => Math.min(current, maxPages)) // update the current page if the new items per page is less than the current page
	}
	return (
		<>
			{loading && (
				<div className='text-gray-400 text-center flex justify-center items-center h-28 text-md m2-10'>
					<ThreeDots
						visible={true}
						height='40'
						width='40'
						color='#4fa94d'
						radius='9'
						ariaLabel='three-dots-loading'
						wrapperStyle={{}}
						wrapperClass=''
					/>
				</div>
			)}
			{data.length !== 0 && !loading ? (
				<div className='relative overflow-x-auto shadow-md sm:rounded-md'>
					<table className='w-full text-sm text-left rtl:text-right text-white border border-darkblueLight rounded-md scrollbar-thin'>
						<thead className='text-xs uppercase text-white bg-darkblueLight py-2'>
							<tr className='px-6 py-3 cursor-pointer '>
								{columns.map((column) => (
									<th
										key={column.key}
										scope='col'
										className='px-6 py-3  hover:text-third-dark transition-all duration-300 ease-in-out'
										onClick={() => requestSort(column.key)}
									>
										{column.label}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{currentData.map((row, index) => (
								<tr
									key={index}
									className={`${index % 2 === 0 ? 'bg-darkblueMedium' : 'bg-transparent'} cursor-pointer text-xs hover:bg-green-900/40  ${row.timeoutInvocations ? 'text-red-500' : ''} ${row.provisionedMemoryMB > row.optimalMemory * 2 ? 'text-yellow-500' : ''}`}
								>
									{columns.map((column) => {
										if (column.key === 'reportID') {
											return (
												<td key={column.key} className='px-6 py-3 '>
													<Link
														to={`/report/reportID=${row[column.key]}`}
														className='text-lambdaPrimary-light hover:underline'
													>
														{row[column.key]}
													</Link>
												</td>
											)
										} else {
											return (
												<td key={column.key} className='px-6 py-3'>
													{row[column.key]}
												</td>
											)
										}
									})}
								</tr>
							))}
						</tbody>
					</table>
					<nav
						className='flex flex-col md:flex-row justify-start md:justify-end pt-8 gap-x-16 gap-y-4 md:gap-y-0 text-green-500'
						aria-label='Table navigation'
					>
						<div className='text-xs lg:text-sm font-light '>
							Showing{' '}
							<span className='font-light text-white px-2'>
								{indexOfFirstItem + 1}
							</span>{' '}
							to{' '}
							<span className='font-light  text-white px-2'>
								{indexOfLastItem > data.length ? data.length : indexOfLastItem}
							</span>{' '}
							{/* of{' '}
							<span className='font-light text-gray-900 dark:text-white px-2'>
								{data.length}
							</span> */}
						</div>
						<div className='flex flex-row'>
							<label
								htmlFor='itemsPerPage'
								className='text-xs lg:text-sm  flex items-center'
							>
								Records / page:
							</label>
							<select
								id='itemsPerPage'
								value={rowsPerPage}
								onChange={handleItemsPerPageChange}
								className='ml-2 px-2 text-white border border-darkblueLight bg-darkblueMedium rounded-md text-xs focus:outline-none focus:ring-0'
							>
								<option value='5'>5</option>
								<option value='10'>10</option>
								<option value='20'>20</option>
								<option value='30'>30</option>
								<option value='40'>40</option>
								<option value='50'>50</option>
								<option value='100'>100</option>
								<option value='200'>200</option>
								<option value='300'>300</option>
								<option value='400'>400</option>
								<option value='500'>500</option>
								<option value='1000'>1000</option>
							</select>
						</div>
						<div className='flex flex-row'>
							<div className='flex items-center md:mt-0 text-white space-x-8 cursor-pointer'>
								<div
									className={`flex flex-row items-center  text-xs lg:text-sm space-x-2 ${currentPage === 1 ? 'text-slate-500' : 'text-white'}`}
								>
									<p>{'<<'}</p>
									<button onClick={handlePrevious} disabled={currentPage === 1}>
										Previous
									</button>
								</div>
								<div
									className={`flex flex-row items-center  text-xs lg:text-sm space-x-2 cursor-pointer ${currentPage === maxPages ? 'text-slate-500' : 'text-white'} `}
								>
									<button
										onClick={handleNext}
										disabled={currentPage === maxPages}
										// disabled={!continuationToken && currentPage === maxPages}
									>
										Next
									</button>
									<p>{'>>'}</p>
								</div>
							</div>
						</div>
					</nav>
				</div>
			) : data.length !== 0 && loading ? (
				<div className='text-gray-400 text-center flex justify-center items-center h-28 text-md mt-10'>
					Loading more data
				</div>
			) : (
				<div className='text-gray-400 text-center flex justify-center items-center h-28 text-md mt-10'>
					No Data Found
				</div>
			)}
		</>
	)
}

export default Home
